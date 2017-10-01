inside_recursion = false;
MAX_RECURSION_DEPTH = 7; // for opening recursively
MAX_SAME_CALL_AUTOOPEN = 3; // some function might be used many times -- but there is no need to autoopen all occasions (as they become apparent) 
autoopen_callcounts = {}; // let it be global

function get_callcount( call_id ){
 autoopen_callcounts[call_id] = autoopen_callcounts[call_id]  || 0;
 return autoopen_callcounts[call_id];
}

function init(){
    
   // jQuery methods go here...
   // $(".inlined").hide();
   
   $first_code =  $("#codes .code").first();
    
   // $("#trace > #entering-call").prepend( $first_code.html() ); // TODO: deprecate "#entering-call"
   $("#trace").prepend( $first_code.prop('outerHTML') );
   
   // togle nested functions
   $(".nested_function").each( function(){
       console.log("bla");
       toggle_inlined($(this), "block"); 
    });
       
   make_wathces_scroll_fixed_header();
   init_4_new_expanded_stuff();
        
    // if( ! (doc_id in localStorage) $("#load-tree").hide(); // but should show it on save


}

function init_4_new_expanded_stuff(){


   // $(".line.visited .line-code").each(
        // function(){  
            // var title = $(this).parent().prop('id');
            // this.title = title;
    // });

   // $(".toggler").each(
        // function(){  
            // call_id = this.id.substr(  "toggler_".length );
            // this.title = call_id;
    // });
    
    $(".toggle-code").off("click").on("click", function(event) { $(this).parent().siblings(".line").toggle(); });  // .not('.func-header') ?
    
    $(".toggle-noncall-lines").off("click").on("click", function(event) { $(this).parents('.code').first().find(".line ").not('.caller').not('.func-header').toggle(); });
    $(".toggle-watches").off("click").on("click", function(event) { $(this).parents('.code').first().find(".watches ").toggle(); });
    
    $(".toggler").off("mouseover").on("mouseover", 
        function(event) { style_inlined(this, "border-width", "3px");  });

    $(".toggler").off("mouseout").on("mouseout", 
        function(event) { style_inlined(this, "border-width", "1px"); return true; });

    // $(".toggler").each( function(){ 
        // bind_tooltip( $(this),  function(){ return $button.prop("title");} ) 
    // } );
    
    $(".show-stack-path").each( function(){ bind_tooltip( $(this), stack_path ) } );
    // $(".show-stack-path").each( function(){ $(this).prop('title', stack_path( $(this) ) ); } );
    
} 



function stack_path($button){
    
   var result = $button.parents(".code")
  .map(function() {
    return this.id.substr(  "code_".length );
  })
  .get();
  
  result.reverse();
  
  return result.join( "<br> " );
  // .join( "&#013;&#010;" );
}

function bind_tooltip($el, content_func){
    $tooltip = $("div.tooltip");
        
    // show /populate
    $el.bind("mouseover", function(event) {
        $tooltip.html( content_func($el) ) .css({
            bottom: $(window).height()-event.pageY + 10 + "px",
            right: $(window).width()- event.pageX -10 + "px"
        }).show();
        return true;
    });
    
    // hide
    $el.bind('mouseout', function(){ $tooltip.hide(); return true; });
    
}

function get_inlined_jq( toggler ){
        var id = toggler.id;
        call_id = id.substr(  "toggler_".length );

        // get corresponding closest container?
        return $(toggler).siblings("#inlined_"+call_id).first();
}

function style_inlined( toggler, prop, val ){
    $target = get_inlined_jq(toggler);
    $target.css( prop, val );
}

function toggle_watch( toggler ){ 
    
    var call_id = toggler.id.substr(  "toggler_".length );
    $(toggler).siblings(".watches").toggle();
        
}
    
function smart_toggle( toggler ){

        toggler = (typeof toggler !== 'undefined') ?  toggler : this;   // defaults to "this" -- element calling the function
        
        $target = get_inlined_jq(toggler);
        if ($target.is(":visible")) {
            $target.hide();  // TODO could refactor to use: toggle_inlined($target, "none");
            $(toggler).addClass("closed").removeClass("opened");
            
        }
        else toggle_inlined($target, "block");
}

function toggle_all_recursively( toggler ){
    autoopen_callcounts = {}; // reset 
    
    var display; // = "none";
    if ($(toggler).hasClass("opened") ){
        display = "none";
        $(toggler).addClass("closed").removeClass("opened") ;
    }
    else{
        $(toggler).addClass("opened").removeClass("closed") ;
        display = "block";
    }
    
    $(toggler).siblings(".inlined").each( function(){
        inside_recursion = true;
        toggle_inlined( $(this), display , true);
        inside_recursion = false;
    });
    
    my_classes = $(toggler).prop("class"); // mowt interesting is opened/closed
    // console.log("my_classes", my_classes);
    // apply state to inner togglers
    // console.log( $(toggler).find(".toggler.recursive") );  // Doesn't find anything ??? //TODO fix
    $(toggler).find(".toggler.recursive").prop( "class", my_classes );
    
}


function toggle_inlined($container, display, recurse, depth){
    
    display = (typeof display !== 'undefined') ?  display : "block"; // default
    recurse = (typeof recurse !== 'undefined') ?  recurse : false; // default
    depth = (typeof depth !== 'undefined') ?  depth : 0; // default
    
    var id = $container.prop('id');
    
    
    // document.title = "DBG: toggle_inlined( " + id +", "+display+", "+recurse+", "+depth+" )"; // DBG
    
    // if (typeof id !== 'undefined'){ // if we don't find valid container
        // console.log( "show all found container with no id", $container);
        // return;
    // }
        
        
    var call_id = id.substr(  "inlined_".length );
    
    if (  inside_recursion ){
        if ( get_callcount(call_id ) >= MAX_SAME_CALL_AUTOOPEN ){
            return;
        }
        autoopen_callcounts[call_id]++; 
    }
    
    var $code = $("#codes #code_"+call_id).first();  // take from #codes list
    
    
    if($container.html().trim()=="") // if empty
    {
        // console.log("DBG: empty inline: ", call_id,  "// toggle_inlined( " + id +", "+display+", "+recurse+", "+depth+")" );
        // if (call_id == "csv2df_emitter-to_float"){
            // console.log("DBG: ???"); // solved by autoopen_callcounts
        // }
        // $container.append(  $code.html() ); // TODO: attr('innerHTML')?? should take initial stuff
        $container.append(  $code.prop('outerHTML') ); // TODO: attr('innerHTML')?? should take initial stuff
        init_4_new_expanded_stuff();
    }
        
    if (display=='block') {
        $container.show();
        make_wathces_scroll_fixed_header();
        $container.siblings("#toggler_"+call_id).first().removeClass('closed').addClass('opened');
    }
    else{
        $container.hide();
        $container.siblings("#toggler_"+call_id).first().removeClass('opened').addClass('closed');
    }
    
    if(recurse && (depth < MAX_RECURSION_DEPTH) ){
        
        $container.find(".inlined").each( function(){
            toggle_inlined($(this), display, true, depth+1);
        });
        
        // $togglers = $container.find(".toggler");
        // $togglers.each( function(){
            // $target = get_inlined_jq(this);
            // toggle_inlined($target,  "block", true, depth+1);
        // });
    }
}

function make_wathces_scroll_fixed_header(){

        //  https://stackoverflow.com/a/25902860/4217317
        var tables = document.getElementsByClassName("watches")
        for (var i = 0; i < tables.length; i++) {
            tables[i].addEventListener("scroll",function(){
               var translate = "translate(0,"+this.scrollTop+"px)";
               this.querySelector("thead").style.transform = translate;
            });
        }
}

function save_expanded_html(){
    html = $("#trace").html();    
    localStorage[ doc_id +"__"+ timestamp ] =  html; 
}
function load_expanded_html(){
    var saved_html = localStorage[ doc_id +"__"+ timestamp ];  
    if (saved_html)
        $("#trace").html( saved_html );  
    else
        alert(" saved view not found for "+doc_id+"__"+timestamp);
}

// for persistance of folded out structure 
function save_expanded_tree_state(){ // TODO: rename to save_expanded_tree_state
    var state_tree = [];
    get_opened_inlines_state_tree( $("#trace"), state_tree);
    state_tree = JSON.stringify( state_tree );
    console.log( "final_state_tree", state_tree );
    localStorage[ doc_id ] =  state_tree;
    
   
}

function load_expanded_tree_state(){
    
    var state_tree = JSON.parse( localStorage[ doc_id ] );
    apply_opened_inlines_state_tree( $("#trace"), state_tree);
 
}



function get_opened_inlines_state_tree($container, info){
    /// $container -- initial / root
    /// info -- the array for tree structure  
    var $expanded_stuff = $container.children(".code").children(".line").children(".inlined:visible");
    // .code should be single node; .line - may; .inlined - single
    if ($expanded_stuff){
        // for(var i=0; i<
        $expanded_stuff.each( function(){
            var $node = $(this);
            var subinlined_id = $node.prop("id");
            var call_id = subinlined_id.substr(  "inlined_".length );
            
            var $line = $node.parent();
            var line_id = $line.prop("id");
            // var $code = $line.parent();
            // var code_id = $code.prop("id");
            var children = [];
            var obj = { line_id:line_id, call_id:call_id, children:children  };
            info.push( obj ); // append possible branch
            // console.log( info );
            get_opened_inlines_state_tree($node, children); // recurse -- fill branch
        });
    }
}

function apply_opened_inlines_state_tree($container, info){
    for (var i = 0; i < info.length; i++) {
        var obj = info[i];
        var $line = $container.children(".code").children("#"+obj.line_id+".line");
        var toggler = $line.children("#toggler_"+obj.call_id ).first()[0]; // non JQ variable
        smart_toggle( toggler ); // should open
        
        var $inlined = $line.children("#inlined_"+obj.call_id ).first()  // JQ var
        apply_opened_inlines_state_tree( $inlined, obj.children );
    }    
}
