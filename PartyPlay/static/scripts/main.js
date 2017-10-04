



 $('#results').on('click', '.button-add', function() {
     var $this = $(this);
     var video_id = $this.attr('id').split(/-(.+)/)[1];

     console.log(video_id);

    $("#results").addClass('hidden');

     // var url = 'https://www.youtube.com/watch?v=' + video_id;
     gapi.client.setApiKey('AIzaSyAZGkCZovLfGCxbDniowVMwHoHfMYcVJWo');
     gapi.client.load('youtube', 'v3', function () {
         getDurationTitleAndAdd(video_id);

     });
     $("#query").val("");
 });


$('#favorite').on('click', '.button-favorite', function() {
    $.ajax({
        url : favorite_url,
        type: "POST",
        data: {},
        success : function(html) {

        }
    });
});

$(document).ready(function()
{
    mouse_is_inside = false;

    $('#results').hover(function(){
        mouse_is_inside=true;
    }, function(){
        mouse_is_inside=false;
    });

    $("body").mouseup(function(){
        if(! mouse_is_inside) $('#results').addClass('hidden');
    });
});

function add_video(video_id, duration, title){
        console.log("add_video is working");
        console.log(video_id);


        $.ajax({
            url : add_url,
            type : "POST",
            data: {'video_id': video_id, 'duration': convert_yt_time(duration), 'title': title },

            success : function(html) {

                console.log("success"); // another sanity check
                $('.table_body').html(html);
                if(current_vid_pk == null){
                    window.clearInterval(interval_id);
                    send_end_video()
                }
            },

            // handle a non-successful response
            error : function(xhr,errmsg,err) {
                $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                    " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
                console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        })


}

 function getDurationTitleAndAdd(video_id) {
    console.log(video_id);
    var request = gapi.client.youtube.videos.list({
        id: video_id,
        part:'snippet, contentDetails',
        maxResults: 10,
        type: 'video'
    });

    request.execute(function(response){
        var items = response.result.items;
        $.each(items, function(index, item) {

            add_video(video_id, item.contentDetails.duration, item.snippet.title);

        })
    });
 }




 function keyWordsearch(){
    gapi.client.setApiKey('AIzaSyAZGkCZovLfGCxbDniowVMwHoHfMYcVJWo');

    gapi.client.load('youtube', 'v3', function() {
            makeRequest();
    });
    $("#results").removeClass('hidden');
}

function makeRequest() {
        var q = $('#query').val();
        var request = gapi.client.youtube.search.list({
                q: q,
                part: 'snippet',
                maxResults: 10,
                type: 'video'
        });
        request.execute(function(response)  {
                $('#results').empty();
                var srchItems = response.result.items;
                $.each(srchItems, function(index, item) {
                    vidTitle = item.snippet.title;
                    vidThumburl =  item.snippet.thumbnails.default.url;
                    vidThumbimg = '<img id="thumb" src="'+vidThumburl+'" alt="No  Image Available." style="width:102px;height:64px">';
                    vidID = item.id.videoId;
                    btn_id = "'btn-" + vidID +"'";
                    add_button = "<button id=" + btn_id +  "class='button-add'><span class='glyphicon glyphicon-plus-sign'></span> Add</button>";
                    console.log(add_button);
                    $('#results').append('<button id=' + btn_id + 'type="button" class="list-group-item list-group-item-action button-add">' + vidThumbimg + ' ' + vidTitle + ' <span class="glyphicon glyphicon-plus-sign"></span></button>');
        })
    })
}


var tag = document.createElement('script');
tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

// creates an iframe and youtube player after the api code downloads

function onYouTubeIframeAPIReady(){


    player = new YT.Player('player', {

        playerVars: {'autoplay':1, 'rel':0}, // 'controls':0, 'start':start},

        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
        }

    });
}

function onPlayerReady(event) {

    send_end_video()
}

function onPlayerStateChange(event){
    if(event.data === 0) {
       // alert('done');
        send_end_video()
    }
}


var interval_id;
function video_timer(time){
    console.log('video timer: ' + time);
    setTimeout(send_end_video, time);

    var x = 0;
    interval_id = setInterval(function(){
        time=time-1000;
        if(time <= 0){
            window.clearInterval(interval_id);
            x=0
        }

    }, 1000)
}

$(setInterval(refresh_queue, 10000));

function refresh_queue(){
    console.log("refreshing queue");

    $('.table_body').html('').load(get_queue_url
        );
    // $.ajax({
    //     url : get_queue_url,
    //     type : "GET",
    //     dataType: 'json',
    //
    //     success: function(data) {
    //
    //         $('.video_and_queue').html(data['html']);
    //     }
    //
    // })
}

function send_end_video(){
    console.log("sending_video_end_data");
    $.ajax({
        url : end_video_url,
        type :"POST",
        data: {
            'vid_pk': current_vid_pk
        },
        dataType:'json',

        success : function(data) {
            console.log("success" + data['time_until_next']);


            current_vid_pk = data['current_vid_pk'];

            if(current_vid_pk != null){
                $('.video_and_queue').html(data['html']);


                $('#current-title').text("Now Playing: " + data['current_vid_name']);
                $('#current-uploader').text("Uploaded by: " + data['current_uploader']);
                $('#player').show();

                player.loadVideoById(data['current_vid_id'], data['start_time'] );


                window.clearInterval(queryTimer)
            }else{
                $('.video_and_queue').html(data['html']);

                $('#player').hide();

                $('#current-title').text("There's nothing here! Add a video to get started.");
                $('#current-uploader').text("");

                window.clearInterval(queryTimer);
                queryTimer = setInterval(send_end_video, 10000 );
            }


        },
        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }


    })
}

function convert_yt_time(duration) {
    var a = duration.match(/\d+/g);

    if (duration.indexOf('M') >= 0 && duration.indexOf('H') == -1 && duration.indexOf('S') == -1) {
        a = [0, a[0], 0];
    }

    if (duration.indexOf('H') >= 0 && duration.indexOf('M') == -1) {
        a = [a[0], 0, a[1]];
    }
    if (duration.indexOf('H') >= 0 && duration.indexOf('M') == -1 && duration.indexOf('S') == -1) {
        a = [a[0], 0, 0];
    }

    duration = 0;

    if (a.length == 3) {
        duration = duration + parseInt(a[0]) * 3600;
        duration = duration + parseInt(a[1]) * 60;
        duration = duration + parseInt(a[2]);
    }

    if (a.length == 2) {
        duration = duration + parseInt(a[0]) * 60;
        duration = duration + parseInt(a[1]);
    }

    if (a.length == 1) {
        duration = duration + parseInt(a[0]);
    }
    return duration
}

$("#searchform").submit(function(){
    keyWordsearch();
    return false
});


$(document).on('submit', "#searchform",function() {
   /* handler code*/
   keyWordsearch()
});

