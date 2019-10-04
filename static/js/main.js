$(document).ready(function () {
    // Init
    $('.image-section').hide();
    $('.loader').hide();
    $('#result').hide();

    // Upload Preview
    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                console.log("onload");
                var image = new Image();
                image.src = e.target.result;
                image.onload = function (imageEvent) {
                    console.log("image onload");
                    console.log("Width: " + this.width);
                    console.log("Height: " + this.height);

                    var c = document.getElementById("myCanvas");
                    //const width = 600;
                    console.log("$(window).width(): " + $(window).width())
                    console.log("$(window).width(): " + $(window).width())
                    console.log("window.screen.width: " + window.screen.width)
                    console.log("window.screen.availWidth: " + window.screen.availWidth)
                    console.log("$(document).width(): " + $(document).width())

                    //const width = $(window).width()/2;
                    //const width = window.screen.width/2;
                    const width = window.screen.availWidth / 2;
                    const scaleFactor = width / image.width;

                    //c.width = this.width;
                    c.width = width
                    c.height = this.height * scaleFactor;
                    var ctx = c.getContext("2d");
                    $('#imagePreview').css("width", width);
                    $('#imagePreview').css("height", this.height * scaleFactor);
                    //ctx.drawImage(image, 0, 0, this.width, this.height);
                    ctx.drawImage(image, 0, 0, width, this.height * scaleFactor);
                    $('.img-preview').css("width", width);
                    $('.img-preview').css("height", this.height * scaleFactor);
                }
                $('#imagePreview').hide();
                $('#imagePreview').fadeIn(650);
                
            }
            reader.readAsDataURL(input.files[0]);
            
        }
    }
    $("#imageUpload").change(function () {
        console.log("change");
        $('.image-section').show();
        $('#btn-predict').show();
        $('#result').text('');
        $('#result').hide();
        readURL(this);
    });

    // Predict
    $('#btn-predict').click(function () {
        var form_data = new FormData($('#upload-file')[0]);

        // Show loading animation
        $(this).hide();
        $('.loader').show();

        // Make prediction by calling api /predict
        $.ajax({
            type: 'POST',
            url: '/predict',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            success: function (data) {
                // Get and display the result
                $('.loader').hide();
                $('#result').fadeIn(600);
                $('#result').text(' Result:  ' + data);
                console.log('Success!');
                function speak(data) {
                    console.log("speak")
	                var msg = new SpeechSynthesisUtterance();
	                msg.text = data;
	                msg.lang = 'en-US';
	                msg.volume = 1; // 0 to 1
	                msg.rate = 1; // 0.1 to 10
	                msg.pitch = 2; //0 to 2
	                speechSynthesis.speak(msg);
                }
                speak(data);
            },
        });
    });

});