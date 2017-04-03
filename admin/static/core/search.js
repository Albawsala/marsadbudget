var $form;
var $path;


var render_fields = function(fields, path, level)
{
	var $select = $('<select name="'+path+'" data-level="'+level+'"></select>')

	for(var i=0; i<fields.length; i++)
	{
		var field = fields[i],
			$field = $('<option value="'+field.name+'" class="type-'+field.type+'" data-type="'+field.type+'">'+field.name+'</option>');

		field.level = level;
		field.path = path+'.'+field.name;
		$field[0].data = field;
		$select.append($field);
	}

	$select.change(function()
	{
		var $this = $(this),
			$field = $this.find('option:selected'),
			field = $field[0].data;

		if(field.children)
		{
			render_fields(field.children, field.path, field.level+1);
			$path.val(field.path);
		}
		else
		{
			cleanup_fields(field.level+1);
			$path.val($this.attr("name"));
		}
	})

	cleanup_fields(level);
	$form.append($select);
	$select.change();
}


var cleanup_fields = function(level)
{
	$form.find('select').each(function()
	{
		var $this = $(this);

		if($this.data("level") >= level)
			$this.remove();
	});
}