sugTemplate.prototype.build70052900 = function(div, data, pdata, xml){
    $(div).addClass("mag-area");
    var context = { "data" : data, "pdata" : pdata, "xml" : xml};
    var $subdisplay = $(xml).find('subitem subdisplay').eq(0);
    context.title = $subdisplay.find('title').text();
    context.url = $subdisplay.find('url').text();
    context.img = this.getSuggCdnImgLink($subdisplay.find('poster').text());
    context.total = $subdisplay.find('update').text();
    context.year = $subdisplay.find('nianfen').text();
    context.area = $subdisplay.find('area').text().replace(/;/g, " ");
    context.leixing = $subdisplay.find('leixing').text().replace(/;/g, " ");
    context.actor = $subdisplay.find('zhuchi').text().split(';');
    context.jianjie = $subdisplay.find('jianjie').text();
    context.bofang = $subdisplay.find('bofangdizhi').text();

    var tempCode ='<h3 class="sug-tit"><a id="sgtitle" href="${url}" id="sg_70052900_title" target="_blank">${title}</a></h3>' +
        '<div class="through-movie">' +
            '<a href="${url}" id="sg_70052900_img" class="tm-img" target="_blank"><img src="${img}" /></a>' +
            '<div class="tm-info">' +
                '<p class="tmi-time"><span>更新至</span>${total}</p>' +
                '<p class="tmi-tags">${year}<span>|</span>${area}<span>|</span>${leixing}</p>' +
                '<p class="zy">主持人：<!--LOOP SET=${actor}--><span>${item}</span><!--ENDLOOP--></p>' +
                '<p class="tmi-txt">简介：${jianjie}</p>' +
                '<p class="tmi-btn"><a href="${bofang}" id="sg_70052900_btn" target="_blank">最新一期</a></p>' +
            '</div>' +
        '</div>';

    this.buildZhiDa(div, context, tempCode);
}
