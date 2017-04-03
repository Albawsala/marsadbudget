
$(function() {
  LocsA = [];
  var projects = $.get('/projects' , function(data){
    project_fun = function(project_id) {
      $('#context_proj').html(data['projects'][project_id]['contexte'][$('html').attr('lang')]);
      $('#contenu_proj').html(data['projects'][project_id]['contenu'][$('html').attr('lang')]);
      $('#Project_title').html(data['projects'][project_id]['titre'][$('html').attr('lang')]);
      $('#cout_proj').html(data['projects'][project_id]['cout_reel']);
      $('#objectif_proj').html(data['projects'][project_id]['objectif'][$('html').attr('lang')]);
      $('#financement_proj').html(data['projects'][project_id]['financement'][$('html').attr('lang')]);
      $('#gov_proj').html(data['projects'][project_id]['gouvernorat'][$('html').attr('lang')]);
      $('#muni_proj').html(data['projects'][project_id]['municipalite'][$('html').attr('lang')]);
      $('#deleg_proj').html(data['projects'][project_id]['delegation'][$('html').attr('lang')]);
      $('#date_deb_proj').html(data['projects'][project_id]['date_deb']);
      $('#progress_proj').html(data['projects'][project_id]['progress']+'%');
      $('#progress_proj').attr({'style':'width:'+data['projects'][project_id]['progress']+'%'});
      $('#secteur_proj').html(data['projects'][project_id]['secteur'][$('html').attr('lang')]);
      $('#minis_proj').html(data['projects'][project_id]['ministere'][$('html').attr('lang')]);
      $('#myModal').modal('show');
    }

    search_proj = function () {
      var gov       = $('#filtre-gov').val();
      var secteur   = $('#filtre-sect').val();
      var ministere = $('#filtre-minis').val();
      var cout      = $('#filtre-cout').val();
      var secteur   = $('#filtre-sect').val();
      LocsA         = [];


      $('#list_proj').html('');
      for(project in data['projects']) {
        // filtres logic
        load_it       = true;
        if( $('#proj_keyword').val() != '') {
          if( data['projects'][project]['titre'][$('html').attr('lang')].search($('#proj_keyword').val()) == -1 )
          {
            load_it = false;
          }
        }
        cout          = data['projects'][project]['cout_reel'];
        if(gov != '') {
          if (data['projects'][project]['gouvernorat'][$('html').attr('lang')] != gov)
          {
            load_it = false;
          }
        }
        if(secteur != '') {
          if(data['projects'][project]['secteur'][$('html').attr('lang')] != secteur) {
            load_it = false;
          }
        }

        if( ministere != '') {
          if(data['projects'][project]['ministere'][$('html').attr('lang')] != ministere) {
            load_it = false;
          }
        }
         if( cout < $( "#slider-range" ).slider( "values", 0 ) || cout > $( "#slider-range" ).slider( "values", 1 )) {
           load_it = false;
         }

        // all filters are valid
        if( load_it) {
          LocsA.push({
            lat: data['projects'][project]['coord']['x'],
            lon: data['projects'][project]['coord']['y'],
            zoom : 8,
            title: data['projects'][project]['titre'][$('html').attr('lang')],
            html: '<h3><a href="#" onclick=\'project_fun('+eval(project)+')\'>'+data['projects'][project]['titre'][$('html').attr('lang')]+'</a></h3>',
            animation: google.maps.Animation.DROP,
          });
          load_it = false;
          css_class = '';
          if($('html').attr('lang') == 'ar' ) {
            css_class = 'pull-left';
          }
          else {
            css_class = 'pull-right';
          }
          $('#list_proj').append('<a href="#"  class="list-group-item list-group-item-warning" onclick=\'project_fun('+eval(project)+')\'>'
          +data['projects'][project]['titre'][$('html').attr('lang')]
          +'<span class="badge pull '+css_class+'">'+data['projects'][project]['cout_reel']+' MDT</span></a>');
        }
      }
      $('#gmap').html('');
      load_map(LocsA);
      $('#nb_proj').html(LocsA.length);
    }

    for(project in data['projects']) {
      LocsA.push({
        lat: data['projects'][project]['coord']['x'],
        lon: data['projects'][project]['coord']['y'],
        zoom : 8,
        title: data['projects'][project]['titre'][$('html').attr('lang')],
        html: '<h3><a href="#" onclick=\'project_fun('+eval(project)+')\'>'+data['projects'][project]['titre'][$('html').attr('lang')]+'</a></h3>',
        animation: google.maps.Animation.DROP,
      });
    }
    load_map(LocsA);
    $('#nb_proj').html(LocsA.length);
    function load_map(locations) {
      var map = new Maplace({
        map_options: {
          zoom: 7,
          set_center: [34.754239, 9.800472],
          backgroundColor : '#f6f6f6',
        },
        styles: {
          'Greyscale':
          [{
            featureType: 'landscape',
            elementType: 'labels',
            stylers: [{
              visibility: 'off'
            }]
          },
          {
            "featureType": "administrative",
            "elementType": "labels",
            "stylers": [{
              "visibility": "off"
            }]
          }
          ,
          {
            featureType: 'transit',
            elementType: 'labels',
            stylers: [{
              visibility: 'off'
            }]
          }, {
            featureType: 'poi',
            elementType: 'labels',
            stylers: [{
              visibility: 'off'
            }]
          }, {
            featureType: 'water',
            elementType: 'labels',
            stylers: [{
              visibility: 'off'
            }]
          }, {
            featureType: 'road',
            elementType: 'labels.icon',
            stylers: [{
              visibility: 'off'
            }]
          }, {
            stylers: [{
              hue: '#00aaff'
            }, {
              saturation: -100
            }, {
              gamma: 2.15
            }, {
              lightness: 12
            }]
          }, {
            featureType: 'road',
            elementType: 'labels.text.fill',
            stylers: [{
              visibility: 'off'
            }, {
              lightness: 24
            }]
          }, {
            featureType: 'road',
            elementType: 'geometry',
            stylers: [{
              lightness: 57
            }]
          }
        ]
      },
      controls_on_map: false,
      locations: locations,
    });
    map.Load();
  }
});
});
