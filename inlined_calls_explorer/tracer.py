import sys
import gc
# import traceback
import inspect
import linecache
import py
from collections import defaultdict, OrderedDict


### GLOBALS
stack_defs_original_indents = []
stack_output_indents = []
last_indent = 0

visited_lines = [] # not to visit the same again.. ID by filnename + lineno
visited_calls = [] # not to visit the same again.. ID by filnename + lineno
call_map = defaultdict(list) # caller_lineID: [funcID1, funcID2..]
watched_values = defaultdict(list) #OrderedDict() # key:val   will be   lineID: table of vars
watched_values_after_exec = defaultdict(list) 
stack_waiting_watched_values_after_exec = [None]; #defaultdict(list) #OrderedDict() # key:val   will be   lineID: list of dicts 
codes = {}  # codes of functions

start_frame = None    # TODO: deprecate?

depth = 0
traced_steps = 0

### end GLOBALS

class ConfigDefault(object):
    MAX_DEPTH = 30
    BUFFER_STDOUT = True
    MAX_TRACED_STEPS = None
    path_rel_out_html = '../out/' # TODO: use fix_path..
    out_html_file = 'mytracer.html'
    
    ############# HOOKS (for overriding) #############
    @classmethod
    def decide_to_trace_call(cls, frame):
        """ decides if call is needed to be traced. could be based on module/function name or line analysis """
        
        # ignore/skip calls that are apparent (TODO think twice if something important is not lost)
        if frame.f_code.co_name in ["<lambda>", "<genexpr>", "<dictcomp>", "<setcomp>", "<listcomp>"]:  # FIXME: seems, sometimes wrong def is taken for listcomp or genexp -- if it is used inside of them, example: listcomp_ = [ x for x in generator_()  ] 
        # if frame.f_code.co_name in ["<genexpr>", "<dictcomp>", "<setcomp>", "<listcomp>"]:  # FIXME: seems, sometimes wrong def is taken for listcomp or genexp -- if it is used inside of them, example: listcomp_ = [ x for x in generator_()  ] 
            return False
            
        if moduleID(frame) in [  "__main__", "tracer" ]:
            if frame.f_code.co_name in ['finish', 'do_trace'] \
            or func_qualname(frame) == "CallTracer.__exit__":
                return False

        return True


    @classmethod
    def inject_watch_pragma(cls, line, frame):
        """ a way to define what to watch  in which line -- based on  regexps 
        uses function qualname and lineID to define line.
        
        and appends #WATCH[_AFTER] pragrma (before analysis/parsing of Watches takes place)"""
            
        return line
        
    @classmethod
    def other_cases(cls, frame, event, arg ):
        # print( "#DBG ignoring", event, lineID(frame) )
        pass
    
############# END CONFIG  ##################




def fileID(frame):
    co = frame.f_code
    filename = co.co_filename    
    return filename
    
def moduleID(frame):  # more readable than fileID
    
    try:
        module = inspect.getmodule( frame.f_code )
        module = module and module.__name__ 
    except Exception as e:
        print("ERROR, no module in frame", e, frame)
        print("...", frame.f_code.co_filename, frame.f_lineno)
        # print(getline(filename, lineno))
        module =  None
    
    return module
    
SEP_4ID = "-"  # separator (or joiner) for ID (module to function or so)
def join_ids( *args ):
    result = SEP_4ID.join( map(str, args))
    # result = result.replace('.', '_' ) # for jquery, not to confuse '.' with classname -- refactored to use jquerify
    return result 
    
def lineID_from_parts(module_id, code_name, lineno):
    return join_ids(module_id, code_name, lineno)
    
def lineID(frame):
    lineno = frame.f_lineno
    # return join_ids(moduleID(frame), lineno)  # to be suitable for HTML DOM ID
    return lineID_from_parts( moduleID(frame), frame.f_code.co_name, lineno )  # to be suitable for HTML DOM ID
    # return (moduleID(frame), lineno)
    # return (fileID(frame), lineno)
    
def funcID(frame):
    qualname = func_qualname(frame)
    module = moduleID(frame)
    return join_ids(module, qualname) #  to be suitable for HTML DOM ID
    # return (module, qualname)
    # return (frame.f_code.co_filename , qualname)
    
def getline(filename, lineno):

    return linecache.getline(filename, lineno )  # it kind of ignores file errors

    """
    try:
        # line = linecache.getline(filename, lineno-1 )
        line = open(filename).readlines()[ lineno-1 ] # to notice file errors
    except FileNotFoundError as e:
        for path in ["<frozen importlib._bootstrap>", "<ipython-input-"]:
            if path in str(e):
                    break
        else:
            print ("FileNotFoundError", e)
    """
                
def format_inspect_stack(stack, start_frame, end_frame):
     # FrameInfo(frame, filename, lineno, function, code_context, index)
    calls = []
    for fi in stack:
        # line = open(fi.filename).readlines()[ fi.lineno-1 ]
        line = getline(fi.filename, fi.lineno )
        
        func_name = fi.frame.f_code.co_name
        calls.insert(0, f'{fi.filename}:{fi.lineno}:{func_name}: {line}' )
        if fi.frame is start_frame:
            break
        
    calls = ['  '*i + "-> " + line for i, line in enumerate( calls ) ] # add indents
    return ''.join( calls )



    
def ajust_indent( line ):
    orig_indent = len(line) - len(line.lstrip())
    if stack_defs_original_indents:
        indent_inside_def = orig_indent - stack_defs_original_indents[-1]
    else:
        indent_inside_def = 0
        
    output_indent = stack_output_indents[-1] if stack_output_indents else 0
    
    new_indent = output_indent + indent_inside_def
    return " " * new_indent  + line.lstrip()

def apply_indent( line ):
    output_indent = stack_output_indents[-1] if stack_output_indents else 0
    return output_indent * ' '   + line

pySource_cache = {}
def get_file_pySource(path):
    # could cash
    if not path in pySource_cache:
        with open(path) as f:
            pySource_cache[path] = py.code.Source( f.read() )
    return pySource_cache[path]

def log(*args, **vars):
    print(*args, **vars)
    
def log_line(frame, extra=""):
    lineno = frame.f_lineno
    co = frame.f_code
    filename = co.co_filename    
    id = lineID(frame)
    if id not in visited_lines:
        line =  ajust_indent( getline(filename,lineno ) )
        global last_indent
        
        def get_current_statement_indent(line):
            return len(line) - len(line.lstrip())
            
            
        def get_first_statement_lineno(filename, lineno):
            s = get_file_pySource( filename )
            # print("DBG src", s)
            if s:
                # print("DBG pySrc line", s.getstatement( lineno ) )  # could do auto dedent...
                statement_start = s.getstatementrange( lineno-1 )[0]  
                return statement_start+1
                
        if lineno == get_first_statement_lineno(filename, lineno):
            # TODO if the call happens not at the end of statement -- use last line indent instead.., 
            last_indent = get_current_statement_indent(line)
            

        line = line.rstrip('\n') +extra
        log( line )
        
    visited_lines.append( id ) # TODO: maybe log only once? or make ordered dict?

    
def get_func_header(frame): 
    co = frame.f_code
    # print("DBG", co )
    try:
        header = inspect.getsourcelines( co )[0][0]
        # print("DBG getsourcelines", inspect.getsourcelines( co ) )
        header = header.rstrip() 
    except TypeError:
        header = None
    return header


def func_qualname(frame):
    
    def backward_compat_qualname(frame): 
        # https://stackoverflow.com/a/2544639/4217317
        def get_class_name(f):
            try:
                return f.f_locals['self'].__class__.__name__
            except KeyError:
                return None
        classname = get_class_name( frame ) 
        
        funcname = frame.f_code.co_name
        if funcname in ["<lambda>", "<genexpr>", "<listcomp>", "<dictcomp>", "<setcomp>" ]:  #https://github.com/gak/pycallgraph/issues/156
            funcname = funcname.replace("<", "[").replace(">", "]") 
            funcname = funcname + '[' + hex(id(frame.f_code)) + ']' +"_"+ str(frame.f_lineno)
            # funcname = funcname + '[' + hex(id(frame.f_code)) + ']' +"_"+ lineID(frame)
            # funcname = lineID(frame)
            
    
        if classname:
            return classname+'.'+funcname
        else:
            return funcname

    try:
        # https://stackoverflow.com/a/45882068/4217317  
        # similar   http://grokbase.com/t/python/python-list/1496vwcab7/qualname-in-python-3-3
        # http://mg.pov.lt/objgraph/
        # https://github.com/wbolster/qualname
        fobj = next( filter(inspect.isfunction, gc.get_referrers(frame.f_code) ) ) # next instead of ..[0]
        result = fobj.__qualname__
        result = result.replace("<", "[").replace(">", "]")
        return result
        """
        # ONLY for methods
        obj = frame.f_locals['self']  
        func_obj = getattr(obj, frame.f_code.co_name)
        return func_obj.__qualname__
        """
    except (KeyError, AttributeError, IndexError):
        
        return backward_compat_qualname(frame)
        return None
        
    # func_obj = frame.f_globals.get(frame.f_code.co_name)
    # qualname = func_obj and func_obj.__qualname__   or ""


def trace_calls(frame, event, arg):
    global start_frame
    global last_indent
    global traced_steps

    traced_steps += 1
    if config.MAX_TRACED_STEPS and traced_steps > config.MAX_TRACED_STEPS:
        traced_steps -= 1
        return
        

    co = frame.f_code
    func_name = co.co_name
    func_line_no = lineno = frame.f_lineno
    filename = co.co_filename
    
    module = moduleID(frame)

    def eval_watches( target_expressions, watch_timeline ):
        """ gets watch expressions values in current frame . Appends them to given watch_timeline table/list """
        # print("#WATCH:", target_expressions, eval(target_expressions, None, frame.f_locals ))
            
        line_watches = OrderedDict()
        for target_expr in map(str.strip, target_expressions):
            # print("DBG locals:",  frame.f_locals )
            try:
                frame.f_globals.update( dict(html=py.xml.html) )
                line_watches[target_expr] = eval(target_expr, frame.f_globals, frame.f_locals )
            # except NameError as e:
            except Exception as e:
                print( "DBG", e, target_expr )
                line_watches[target_expr] = str(e)
            print("#WATCH:", target_expr, line_watches[target_expr] )
            # print("#WATCH:", target_var, frame.f_locals[target_var]) # wouldn't allow expressions
        
        if not watch_timeline: # it is table with headers in first row
            watch_timeline.append( target_expressions )
        watch_timeline. append( list( line_watches.values() ) )
        
        return line_watches

    if event == 'line':
        
        log_line( frame )#, extra=f"  # line: {frame.f_lineno}, {frame.f_locals}   #module {module}" )
        
                
        def track_watches():
            """ uses #WATCH[_AFTER] pragmas to take expression snapshots 
            Default WATCH takes the value before line execution (default settrace behaviour)
            WATCH_AFTER takes the value AFTER line execution (this is more robust (possibly buggy), as execution can jump into another function call before finishing)
            """
            ### watch after exec init  finally previous
            waiting_watches = stack_waiting_watched_values_after_exec[-1]
            if waiting_watches:
                line_id, target_expressions = waiting_watches
                eval_watches( target_expressions, watch_timeline=watched_values_after_exec[line_id] )
                stack_waiting_watched_values_after_exec[-1] = None
                                        
            line = getline( filename, lineno) 
            line = config.inject_watch_pragma( line, frame  ) # do WATCH INJECTION - a way to ask to watch something without touching target code
            
            line_id = lineID( frame )
            # target:         df = df.pivot(columns='label', values='value', index='time_index') # in emitter.py:get_dataframe(..)

            for pragma in ['#WATCH:', '#WATCH_AFTER:' ]:
                if pragma  in  line:
                    target_expressions = line.split( pragma )[-1].strip()
                    target_expressions = target_expressions.split(';')  # todo use AST?
                    
                    if pragma == '#WATCH:':
                        # print("inspect STACK\n")
                        # print(format_inspect_stack( inspect.stack()[1:], start_frame, end_frame=frame  )   )
                        eval_watches( target_expressions, watch_timeline=watched_values[ line_id ] )
                    
                    if pragma == '#WATCH_AFTER:':                            
                        ### watch after exec init
                        stack_waiting_watched_values_after_exec[-1] = ( (lineID(frame), target_expressions) )
           
        
        track_watches()
        return trace_calls 

    elif config.decide_to_trace_call(frame):
    # if True:
        
        """
        #skip if already visited
        if lineID(frame) in visited_calls:  # TODO: allow duplicate visits -- as it may mean different lines inside call
            # if event == 'call':
                # print( apply_indent( last_indent*' ' + '#@skip_inline (already visited)') )
            pass
            # FIXME: TODO deprecate -- as when calling it should include "caller line" -- better use call_map
            # return trace_calls    
            
        else:
            visited_calls.append( lineID(frame)  )  # now this includes returns as well...
        """    
        
    

        global depth
        
        if event == 'call':
            # print("DBG call", filename, lineno)

            depth += 1

            if depth < config.MAX_DEPTH:
                

                header = get_func_header( frame ) 
                if header is None:
                    print("DBG no function header", filename, lineno)
                    return trace_calls
                # else:
                    # print("DBG HEADER", header)

                stack_output_indents.append( last_indent )  
                # print("DBG last_indent", last_indent, stack_output_indents)
                orig_indent = len(header) - len(header.lstrip() )
                stack_defs_original_indents.append( orig_indent ) 
                
                stack_waiting_watched_values_after_exec.append( None )
                
                # print("Header orig_indent", header, orig_indent)
                header = apply_indent( header.lstrip() ) # should go here:  after  orig_indent and  before append            
                qualname = func_qualname(frame)
                fID = funcID( frame )
                    
                if not fID in codes:
                    codes[ fID ] = inspect.getsourcelines( frame.f_code )
                
                
                log( apply_indent( f"#@inline {depth}: {module}. {qualname} " ))
                log( header )

               
                def inspect_caller(frame):
                    caller = frame.f_back
                    if caller is None:
                        log ("DBG, strange, caller is None", frame, lineID(frame) )
                        return 
                    else:
                        caller_lineno = caller.f_lineno
                        caller_filename = caller.f_code.co_filename
                        # print( apply_indent( f"#@caller {caller_lineno} @{caller_filename} " ))
                        
                        called_from_line = call_map[ lineID(caller) ]
                        if fID not in called_from_line: 
                            called_from_line.append( fID )
                    
                        if func_name == 'get_dataframes': # TODO -- make option..
                            global start_frame
                            start_frame = caller
                inspect_caller(frame) 
                
            return trace_calls
            
        elif event == 'return':
            if depth < config.MAX_DEPTH:
                # print (apply_indent( '#@inline_end'))
                def head( val, cnt=30 ):
                    val = str(val)
                    if len(val) > cnt:
                        val = val[:cnt]+"..."
                    return val
                    
                
                retval = arg
                log (apply_indent( '#@return: %s => %s' % (func_name, head(retval) )))
                
                # if stack_defs_original_indents: stack_defs_original_indents.pop()
                stack_defs_original_indents.pop()
                # if stack_output_indents: stack_output_indents.pop()
                last_indent = stack_output_indents.pop()
                
                waiting_watches = stack_waiting_watched_values_after_exec.pop()
                ### watch after exec init  finally previous
                if waiting_watches:
                    line_id, target_expressions = waiting_watches
                    eval_watches( target_expressions, watch_timeline=watched_values_after_exec[line_id] )
                
                # last_indent = stack_output_indents[-1]
                
            depth -= 1
        
        else:
            print("DBG WEIRD EVENT", event, frame.f_code)
    else:
        config.other_cases( frame, event, arg )
        # print( "#DBG ignoring", event, lineID(frame) )
        


############# SOME post processing  ##################

NESTING_SEP = ".[locals]."
def get_nested_functions():
    """
    Helps better see watches..
    As by default in html the watches are shown only in separately listed functions (so nested functions doesn't show watches)
    """
    
    global nested_functions # will list all (first level) nested functions inside each called function
    nested_functions = defaultdict(list) # USE: by qualname (in codes id) detect the nesting (and in html replace txt with inlined)  

    def split_parent_id_from_child(id):
        parent, child = None, None
        if NESTING_SEP in id:
            parent, child = id.rsplit( NESTING_SEP, 1 )
        return parent, child
    
    
    for id in codes.keys():
        if not NESTING_SEP in id:
            continue
        child_id = id
        parent_id, child_name = split_parent_id_from_child( child_id )
        nested_functions[parent_id].append( child_id )
        
        # nested_replace(parent_id, child_id)
    return nested_functions
    
        
def nested_function_relative_range(parent_id, child_id):
    ch_lines, ch_start_nr = codes[child_id]  # child  info
    p_lines, p_start_nr = codes[parent_id]  # parent info
    
    replacement_start = ch_start_nr - p_start_nr
    replacement_end =  replacement_start + len(ch_lines)
    return replacement_start, replacement_end
    

def test_nested_replace():
    nested_functions = get_nested_functions()

    for parent_id, nested in nested_functions.items():
        for child_id in nested:
            
            child_name = child_id.rsplit( NESTING_SEP, 1 )[1]
            p_lines, p_start_nr = codes[parent_id] 
            
            start, end = nested_function_relative_range(parent_id, child_id)
            for i in range( start, end ):
                p_lines[i] = '# '+ child_name + " replaced:  " + p_lines[i]
        
    import json
    print("DBG Codes:\n", json.dumps( codes, indent=2) )



############# CONTEXT manager API ##################



import sys


from io import StringIO # grab stdout https://stackoverflow.com/a/45567127/4217317  

def init():
    """start tracing"""
    
    if config.BUFFER_STDOUT:
        # swap stdout
        global stdout
        stdout = sys.stdout
        sys.stdout = fake_stdout = StringIO()
    
    sys.settrace(trace_calls)

def finish():
        sys.settrace(None)
        try:
            output = sys.stdout.getvalue()
                
            if config.BUFFER_STDOUT:
                sys.stdout = stdout  # return stdout
            
            print( output )
            
            # with open('out_inlined.py', 'w') as f: # deprecated
                # f.write( output )

        except AttributeError as e:
            print( e )
            
        finally:
            output_html()
 

def output_html():
    """output after finish"""

     
    if __name__ == "__main__":
        import render 
        import helpers
    else:
        from . import render , helpers
        
    # monkeypach inject some stuff
    render.SEP_4ID = SEP_4ID
    render.join_ids = join_ids
    render.nested_function_relative_range = nested_function_relative_range
    render.lineID_from_parts = lineID_from_parts
    render.config = config
    config.path_rel_out_html = helpers.mypath( config.path_rel_out_html )
    
    html = render.render_html(visited_lines, codes, call_map, watched_values, watched_values_after_exec, get_nested_functions() )
    with open(config.path_rel_out_html + config.out_html_file, 'w') as f:
            f.write( html )


def do_trace( function ):

    init()
    
    try:
        print()
        function()  # enter the CODE
        
    finally:
        finish()
   

# refactor to use contextmanager
import contextlib

class CallTracer(contextlib.AbstractContextManager):
    # def __init__(self):
        # pass
        
    def __enter__(self):
        init()
        return self
        
        
    def __exit__(self,  exc_type, exc_value, traceback):
        finish()
        

config = ConfigDefault

if __name__=="__main__":
    # tests
    
    import sys
    sys.path.append( '../tests')
    import code_simple

    with CallTracer():
        code_simple.B()
        

    test_nested_replace()

