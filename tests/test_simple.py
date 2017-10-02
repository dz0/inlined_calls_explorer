"""defines what code to trace 
and what expressions in which lines or watch"""
# import ..inlined_calls_explorer.main as tracer
import sys
sys.path.append('..')
from inlined_calls_explorer import tracer
# from tracer import moduleID, lineID, funcID, join_ids, ConfigDefault


class ConfigCustom(tracer.ConfigDefault):
    out_html_file = 'mytracer_simple.html' # output file
    
    @classmethod
    def decide_to_trace_call(cls, frame):
        """ decides if call is needed to be traced """

        module = tracer.moduleID(frame)
        if module and module.startswith('test_mytracer'):
           return True 
           
        return super()
        # if frame.f_code.co_name in ["<lambda>", "<genexpr>", "<dictcomp>", "<setcomp>", "<listcomp>"]:  # FIXME: seems, sometimes wrong def is taken for listcomp or genexp -- if it is used inside of them, example: listcomp_ = [ x for x in generator_()  ] 
            # return False
        

    @classmethod
    def inject_watch_pragma(cls, line, frame):
        """ a way to define what to watch  in which line -- based on  regexps 
        uses function qualname and lineID to define line.
        
        and appends #WATCH[_AFTER] pragrma (before analysis/parsing of Watches takes place)"""
        
        
        inject = ""
        if frame.f_code.co_name == "A":
            # let's try to automatically detect assignments (in very primitive way, better would be to use AST)
            if '=' in line and   not '==' in line:
                parts = line.split('=')
                if len(parts) == 2:
                    inject = " #INJECTED #WATCH_AFTER: " + parts[0]                
        return line + inject

    @classmethod
    def other_cases(cls, frame, event, arg ):
        print( "#DBG ignoring", event, tracer.lineID(frame) )


tracer.config = ConfigCustom  # Override/monkey patch config/hooks

import code_simple

with tracer.CallTracer():
    code_simple.B()
    
# def test_simple():    test_mytracer_simple.B()   # wrap
# tracer.do_trace( test_simple )
