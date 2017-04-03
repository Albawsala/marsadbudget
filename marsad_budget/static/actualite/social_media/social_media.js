
function fb_partage(id,link) {
	if(link==null){
		//alert("link is null");
		link = this.document.URL;
		//alert(link);
	}
	
	if (this.document.getElementById(id)){
	//lert(id);alert(link);
    	this.document.getElementById(id).src ="https://www.facebook.com/plugins/share_button.php?href="+link+"&layout=box_count&size=small&mobile_iframe=true&appId=1430676967240081&width=72&height=40";
	this.document.getElementById(id).id=id+'1';}
}

