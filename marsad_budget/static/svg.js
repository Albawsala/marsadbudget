var svgNS = "http://www.w3.org/2000/svg";


var hasClassSVG = function (ele,cls)
{
    var ele_cls = ele.getAttribute('class') || "";
    return ele_cls.match(new RegExp('(\\s|^)'+cls+'(\\s|$)'));
}


var addClassSVG = function (ele,cls)
{
    if(!hasClassSVG(ele, cls))
    {
        var cls_old = ele.getAttribute('class') || "";
        ele.setAttribute('class', cls_old +" "+ cls);
    }
}


var removeClassSVG = function (ele,cls)
{
    var reg = new RegExp('(\\s|^)'+cls+'(\\s|$)'),
        cls_old = ele.getAttribute('class') || "";
    ele.setAttribute('class', cls_old.replace(reg,' '));
}
