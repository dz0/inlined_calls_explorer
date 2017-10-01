import json
import py

def jqueryfy(id):
    """replace tricky characters to underscores"""
    import re
    result = re.sub(r"[.<>\[\] ]", '_', id)
    # print("DBG: jquerify", result)
    return result

def render_html(visited_lines, codes, call_map, watched_values, watched_values_after_exec, nested_functions):
    
    inline_container_tpl = """<div class='inlined' id='inlined_{code_id_jq}' style="margin-left: {indent}ch;"></div>"""
    
    def inlines_tpl( line_id , indent):
        if line_id not in call_map:
            return ""
            
        calls = call_map[ line_id ] # get calls from current line
        togglers = []
        inline_containers = []
        for code_id in calls:  
            code_id_jq = jqueryfy(code_id)
            toggler = f"""
                            <span class='toggler button' id='toggler_{code_id_jq}' title='toggle inlined: {code_id}'
                                onclick='smart_toggle(this)' >&#8597;</span>"""
            inline_container = inline_container_tpl.format( code_id_jq=code_id_jq, indent=indent) 
            
            togglers.append( toggler )
            inline_containers.append( inline_container )
        
        if togglers:
            expand_all = f"""<span class='toggler recursive button closed' id='toggle_all_recursively_{code_id_jq}' title='expand/toggle all calls (recursively)'
                                onclick='toggle_all_recursively(this)'>&#8597;&#8597;&#8597;</span> """
            togglers.append( expand_all )
            
        return ('\n'.join(togglers) + 
                '\n\n' +
                '\n'.join(inline_containers) 
                )
       
    def watches_tpl( line_id, indent ):
        watches = watched_values.get( line_id )    
        watches_after = watched_values_after_exec.get( line_id )    
        def gen_html_table( mtx ):
            from py.xml import html
            # print("DBG genhtmltable", mtx)
            result  = html.table(
                html.thead( html.tr( [html.th( x ) for x in mtx[0] ] ) ),  # header
                html.tbody( 
                        *[ html.tr( [html.td( x ) for x in row] )   # rows
                            for row in mtx[1:] ] 
                            ),
                class_="fixed_headers"
            ) 
            # make it fixed height scrollable # https://codepen.io/tjvantoll/pen/JEKIu
            # result = str(result) + """
            # """
            return str(result) 

        container_before, container_after, toggler = "", "", ""
        if watches:
            # watches = json.dumps( watches )
            # watches = gen_html_table( watches ) + "\n\n"+ gen_html_table( watches_after ) 
            watches_before = watches = gen_html_table( watches ) 
            container_before = f"""<div class='watches before' id='watches_before_{line_id}' title='watches before: {line_id}' style="margin-left: {indent}ch;">{watches_before}</div>"""
        if watches_after:
            watches_after = gen_html_table( watches_after ) 
            container_after = f"""<div class='watches after' id='watches_after_{line_id}' title='watches after: {line_id}' style="margin-left: {indent}ch;">{watches_after}</div>"""
        
        if watches or watches_after:
            toggler =   f"""<span class='button watch-toggler' id='toggler_watches_{line_id}' title='toggle watched expressions (before/after line execution)'
                                onclick='toggle_watch(this)' >&#128269;</span>"""

        return container_before, container_after, toggler

        
    def line_tpl(line, line_id, is_func_header=False):
        line_id_jq = jqueryfy(line_id)
        visited = "visited" if line_id in visited_lines  else ""
        caller = "caller" if line_id in call_map  else ""
        func_header = "func-header" if is_func_header  else ""
        
        indent = len(line)-len(line.lstrip())
        inlines = inlines_tpl( line_id, indent )
        watches_before, watches_after, watches_toggler = watches_tpl( line_id, indent )
        return f"""<div id='{line_id_jq}' class='line {visited} {caller} {func_header}'>
                {watches_before}
                <span class="line-code" title='{line_id}'>{line}</span>  
                {watches_toggler} 
                {inlines} 
                {watches_after}
                </div>"""
        
    def code_tpl(id, code):
        """code is inspect.sourcelines"""
        lines, start_lineno = code
        lines = lines[:]
        # code_id = id
        # print("DBG ID", id)
        module_id, func_qualname = id.split(SEP_4ID)
        func_name = func_qualname.split('.')[-1]
        id_jq = jqueryfy( id )
        
        def syntax_highlight(src):
            from pygments import highlight
            from pygments.lexers import Python3Lexer as PythonLexer 
            from pygments.formatters import HtmlFormatter

            formatter = HtmlFormatter(cssclass="code", nowrap=True)
            result = highlight(src, PythonLexer(encoding="utf-8"), formatter)
            
            # remove: <div class="code"><pre> and corresponding endings
            # start = '<div class="code"><pre>'
            # finish = '</div></pre>'
            
            return result

        
        def dedent_and_highlight(lines):
            orig_code = ''.join(lines) 
            dedented_code = str( py.code.Source( orig_code) )
            # dedented_code = orig_code
            
            # print( "dedented_code\n", dedented_code)
            dedented_code = syntax_highlight( dedented_code )
            
            lines = dedented_code.split("\n") # will loose \n at the ends...
            # print( 'DBG dedent', orig_code, dedented_code, dedented_code, lines )
            return lines
        
        if "<lambda>" not in lines[0]:
            lines[0] = lines[0].rstrip('\n') + "     # "+id +'\n' # inject comment about it's origin
        lines = dedent_and_highlight(lines) 
        
        
        # https://en.wikipedia.org/wiki/Template:Unicode_chart_Arrows
        mini_controlls_panel = """
                        <div class="mini_controlls_panel">
                            <span class="show-stack-path button" title="show call stack"> ⇶ </span> 
                            <span class="toggle-code button" title="toggle code locally"> ↕ </span> 
                            <span class="toggle-noncall-lines button" title="toggle non calling lines"> ⇢ </span> 
                            <span class="toggle-watches button" title="toggle watches"> 🔍 </span> 
                        </div>
                        """
        
        def find_header_nr(lines):
            for nr, line in enumerate(lines):
                if ":" in line: 
                    return nr 
        
        header_nr = find_header_nr(lines)
        html_lines = [line_tpl(x, 
                            line_id=lineID_from_parts(module_id, func_name, start_lineno+nr), 
                            is_func_header=  nr<=header_nr ) 
                            for nr, x in enumerate(lines) ]
        
        def nested_functions_replace_with_refs():
            # TODO: could run twice -- to empty lines before syntax highlight, and then to replace with ref
            parent_id = id
            for child_id in nested_functions[id]:
                                    
                start, end = nested_function_relative_range(parent_id, child_id)
                lines[start:end] = [""]* (end-start)
                
                lines[start] = "REF: "+child_id
                
                orig_lines = code[0]
                line = orig_lines[start]
                indent = len(line)-len(line.lstrip())
                code_id_jq = jqueryfy(child_id)
                
                inlined = inline_container_tpl.format( code_id_jq=code_id_jq, indent=indent )
                # nested_inlined = f"""<div class='nested_function'>{inlined}</div>""" 
                nested_inlined = inlined.replace("class='", "class='nested_function ") # FIXME: bug-prone -- injection shoud be more visible
                # lines[start] =  nested_inlined
                html_lines[start] =  nested_inlined
                            
        nested_functions_replace_with_refs()  # TODO: get inlined out of code-line span -- make it sibling..


        html_code = mini_controlls_panel + ''.join( html_lines )
        return f"""
    <h4>{id}</h4>
    <div id='code_{id_jq}' class='code'>
    {html_code}
    </div>
        """



    codes_html = '\n\n'.join([ code_tpl(id, code) for id, code in codes.items()] )

            
    html = open(config.path_rel_out_html+'mytracer.tpl.html').read()
    html = html.replace("{{codes}}", str(codes_html) )
    
    # html = html.replace("{{visited_lines}}", str(visited_lines) )  # FIXME: deprecated?
    # html = html.replace("{{call_map}}", json.dumps(call_map, indent=4) )
    
    from datetime import datetime as dt
    html = html.replace("{{timestamp}}", str(dt.now() ) )  # use timestamp 
    html = html.replace("{{doc_id}}", str( list(codes.keys())[0] ))  # entering-call id
    
    from pygments.formatters import HtmlFormatter
    html +=  "\n\n<style>\n%s\n.code  { background: #fff; }\n</style>" % HtmlFormatter().get_style_defs('.code')
    
    return html
    # with open('mytracer.html', 'w') as f:
        # f.write( html )
