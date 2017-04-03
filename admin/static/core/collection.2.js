var types = ["string", "numeric", "choice", "options", "boolean", "object", "reference", "file", "yaml"],
    t_string =  ["simple", "multiline", "formated", "email", "url", "list"],
    t_numeric = ["integer", "float", "date", "datetime"];
    
var disable = {
    featured :{
        options: true,
        object: true,
        file: true,
    }
};

var schema;


var set_setup = function(setup, type)
{
    setup.children().removeClass('disabled');
    if (type in disable.featured){ 
        setup.children('#featured').addClass('disabled');
    }
    if (type != "string"){
        setup.children('#multilang').addClass('disabled');
    }
}


var renderField = function(){
    var 
    field =             $('<div class="field new"></div>'),
    fieldrow =          $('<div class="row"></div>'),
    add_command =       $('<span class="trigger clone"></span>'),
    del_command =       $('<span class="trigger del"></span>'),
    key_attr =          $('<input type="text" name="key" placeholder="key"/>'),
    label_attr =        $('<input type="text" name="label" placeholder="label"/>'),
    type_attr =         $('<select name="type"></select>'),
    string_attr =       $('<select name="string-type"></select>'),
    numeric_attr =      $('<select name="numeric-type"></select>'),
    reference_attr =    $('<input type="text" name="reference-collection" placeholder="collection"/>'),
    object_attr =       $('<input type="text" name="object-type" placeholder="class"/>'),
    options_attr =      $('<textarea class="clearfloat" name="options" placeholder="ID,optFR,optAR"></textarea>'),
    setup_block =       $('<div id="setup"></div>'),
    condition_attr =    $('<textarea class="float" name="condition" placeholder="field:value"></textarea>');
    
    // add-del buttons
    add_command.click(function(event){ field.after(renderField()); });
    del_command.click(function(event){ field.remove(); });
    
    // type field
    for(var i=0; i<types.length; i++)
        type_attr.append('<option value="' + types[i] + '">' + types[i] + '</option>')
    
    // string field
    for(var i=0; i<t_string.length; i++){
        string_attr.append('<option value="'+ t_string[i] +'">'+ t_string[i] +'</option>')}
    
    // numeric field
    for(var i=0; i<t_numeric.length; i++){
        numeric_attr.append('<option value="'+ t_numeric[i] +'">'+ t_numeric[i] +'</option>')}
    
    // setup field
    setup_block.append('<span id="featured">F</span>')
               .append('<span id="multiple">M</span>')
               .append('<span id="multilang">L</span>')
               .children().click(function(){ $(this).toggleClass('on'); });
    
    // on type change
    type_attr.change( function(){
        var _type = $(this).val();
        field.children('.field').remove();
        string_attr.hide();
        numeric_attr.hide();
        options_attr.hide();
        reference_attr.hide();
        object_attr.hide();
        if     (_type == "object")   { object_attr.show(); field.append(renderField()); }
        else if(_type == "string")   { string_attr.show(); }
        else if(_type == "numeric")  { numeric_attr.show();}
        else if(_type == "choice")   { options_attr.show(); }
        else if(_type == "options")  { options_attr.show(); }
        else if(_type == "reference"){ reference_attr.show(); }
        set_setup(setup_block, _type);
    });

    // DEFAULT CONF
    numeric_attr.hide();
    options_attr.hide();
    reference_attr.hide();
    object_attr.hide();
    
    // field contruction
    fieldrow.append(add_command)
            .append(setup_block)
            .append(key_attr)
            .append(label_attr)
            .append(type_attr)
            .append(string_attr)
            .append(numeric_attr)
            .append(reference_attr)
            .append(object_attr)
            .append(condition_attr)
            .append(del_command)
            .append(options_attr);

    field.append(fieldrow);
    
    return field;
};

var walkPath = function(path){
    var obj = schema, parts;
    if (path) {
        parts = path.split('.');
        while (parts.length && obj)
            obj = obj[parts.shift()];
    }
    return obj;
};


var addField = function(path, key, label, type, options, condition, setup, old)
{
    var obj = walkPath(path);
    obj._order.push(key);
    obj[key] = {'_label': label, '_type': type, '_setup': setup, '_condition': condition};
    if(old){
        obj[key]['_old'] = true;
    }
    if (type == "object")
        obj[key]['_order'] = [];
    if (type != "boolean" && type != "file" && type != "yaml")
        obj[key]['_options'] = options;
};


var in_array = function(array, value){
    for(i=0;i<array.length;i++){ if(array[i] == value) return true; }
    return false;
}


var split = function(val){
    var splited = val.split('\n'),
        res = new Array();
    
    for(i=0; i<splited.length; i++)
        if(splited[i]) res.push(splited[i]);
    
    return res;
}


var processSchema = function(root, path)
{
    root.find('> .field > .row').each(function(){
        var field = $(this), key, type, options, setup=[],
            condition = split(field.children('textarea[name="condition"]').val()),
            label = field.children('input[name="label"]').val();
        
        if (field.parent().hasClass('new')){
            key = field.children('input[name="key"]').val();
            type = field.children('select[name="type"]').val();
            if (type == "string")
                options = field.children('select[name="string-type"]').val();
            else if (type == "numeric")
                options = field.children('select[name="numeric-type"]').val();
            else if (type == "reference")
                options = field.children('input[name="reference-collection"]').val();
            else
                options = null;
            old = false;
        } else {
            key = field.children('#key').text();
            type = field.children('#type').text();
            old = true;
        }
        
        if (type == "choice" || type == "options")
            options = split(field.find('textarea[name="options"]').val());
        else if (type == "object")
            options = field.children('input[name="object-type"]').val();
        
        field.find('#setup .on').not('.disabled').each(function(){ setup.push($(this).attr('id')) });
            
        addField(path, key, label, type, options, condition, setup, old);
        
        if (type == "object") {
            newpath = (path) ? path +'.'+ key : key;
            processSchema(field.parent(), newpath);
        }
    });
};
