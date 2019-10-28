<p align="center"><img src="https://github.com/dirkh24/mmwml-week5/blob/master/media/Imageguru2.PNG" width="256px"><p>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;

# Imageguru

Imageguru helps you to see a picture when you can't see it with your eyes. 

Make a photo with the app or upload a picture and hear the description what's in the foto!!

# Preview Images

## Login / Register for the service
<p align="center"><img src="https://github.com/dirkh24/mmwml-week5/blob/master/media/Login.PNG"><p>
  
## Choose a plan
<p align="center"><img src="https://github.com/dirkh24/mmwml-week5/blob/master/media/Index.PNG"><p>
  
## Enter your pay data
<p align="center"><img src="https://github.com/dirkh24/mmwml-week5/blob/master/media/pay.png"><p>

## Upload a image
<p align="center"><img src="https://github.com/dirkh24/mmwml-week5/blob/master/media/analyze_image.png"><p>

## The Result
<p align="center"><img src="https://github.com/dirkh24/mmwml-week5/blob/master/media/analyze_image_result.png"><p>


# Instructions on testing the webapp
1. Go to https://imageguru.herokuapp.com/
2. Login with the email admin@admin.com and password admin
3. Choose a plan. For Premium Plan type in the stripe test data (email: admin@admin.com, cardnumber: 4242 4242 4242 4242, date: 01/21 and cvc 545)
4. You're ready to upload your image, prress the predict button and hear the result.

## Setup
``` 
git clone https://github.com/dirkh24/imageguru
cd imageguru
pip install -r requirements.txt
python app.py
```
