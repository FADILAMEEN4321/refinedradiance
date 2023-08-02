$(document).ready(function () {
     
     $('.payWithRazorpay').click(function (e){
        e.preventDefault();
 
        var full_name = $("[name='full_name']").val();
        var phone_number = $("[name='phone_number']").val();
        var address = $("[name='address']").val();
        var token = $("[name='csrfmiddlewaretoken']").val();

        if(full_name == "" || phone_number == "" )
        {
            Swal.fire("Alert!", "All fields are mandatory", "error");

            return false;
        }
        else
        {
            $.ajax({
                method: "GET",
                url: "/proceed-to-pay",
                success: function(response) {
                    // console.log(response);
                    var options = {
                        "key": "rzp_test_XIU51B7eXlouTx", // Enter the Key ID generated from the Dashboard
                        "amount": 1*100 ,//response.total_price * 100, // Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
                        "currency": "INR",
                        "name": "Refined Radiance.", //your business name
                        "description": "Thank you for shopping with us.",
                        "image": "https://example.com/your_logo",
                        // "order_id": "order_9A33XWu170gUtm", //This is a sample Order ID. Pass the `id` obtained in the response of Step 1
                        "handler": function (responseb){
                            // alert(responseb.razorpay_payment_id);
                            data = {
                                "full_name": full_name,
                                "phone_number": phone_number,
                                "address": address,
                                "payment_mode":"Paid by Razorpay",
                                "payment_id": responseb.razorpay_payment_id,
                                csrfmiddlewaretoken: token
                            }
                            $.ajax({
                                method: "POST",
                                url: "/placeorder",
                                data: data,
                                success: function (responsec) {
                                    Swal.fire("Congratulations!", responsec.status , "success").then((value) =>{
                                         window.location.href = '/orders'
                                    });
                                        
                                  

                                }

                            });

                        },
                        "prefill": { //We recommend using the prefill parameter to auto-fill customer's contact information, especially their phone number
                            "name": full_name, //your customer's name
                            "email": "your.sample@example.com", 
                            "contact": phone_number  //Provide the customer's phone number for better conversion rates 
                        },
                        
                        "theme": {
                            "color": "#3399cc"
                        }
                    };
                    var rzp1 = new Razorpay(options);
                    rzp1.open();

                }

            });

           


        }

     })

})