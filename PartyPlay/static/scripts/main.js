


$('#video_list').on('click', '.button-item', function(){
    var $this = $(this);
    var v_id = $this.attr('id').split('-')[1];
    console.log(v_id);

    $('.table_body').html('').load("/partyplay/vote/?vid_pk=" + v_id
    );
});

