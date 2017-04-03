
$.get( "resources_raw/2017/LF/"+$("html").attr('lang'), function( data ) {
  new BubbleTree({
    data: data,
    container: '.bubbletree'
  });
});
