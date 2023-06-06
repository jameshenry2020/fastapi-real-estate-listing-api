from fastapi import APIRouter, Response, status, Depends, HTTPException, Response,BackgroundTasks
from .. import schema, sql_query, util, jwt_auth, models
from ..database import get_db
from jose import JWTError 
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm



router=APIRouter(
    prefix="/api/v1/auth",
    tags=['User Authentication']
)

@router.post('/signup', status_code=status.HTTP_201_CREATED)
async def register_user(user: schema.UserCreate,  background_tasks:BackgroundTasks, db: Session = Depends(get_db)):
    #check if user with that email already exist
    result=sql_query.check_user_exist(db, email=user.email)
    if result: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"user with this email already exist")

    user.password=util.hash_password(user.password)
    #add user to the database
    new_user= sql_query.insert_new_user(db=db, user=user)
    #send verification email to user 
    otpcode=util.generate_otp()
    print(otpcode)
    #add the otp and user_id to the otp model
    message="""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
        </head>
        <body>
            <div style="width: 100%; font-size: 16px; margin-top: 20px; text-align: center;">
                <h1>Email Verification</h1>
                <p>please verify  your email {0:}, with the otp code below,</p><br/>
                  <span href="http://127.0.0.1:8000/api/v1/reset-password?reset-token={1:}" style="margin: 10px 6px; font-size: 16px; box-sizing:border-box; background:#f2f2f2;">{1:}</span>  
                <p>please note the otp code expires in 60 seconds after which its becomes invalid</p>
            </div>
        </body>
        </html>  
    """.format(new_user.email, otpcode)
    otpdata=schema.OTPData
    otpdata.code=otpcode
    otpdata.user_id=new_user.id
    
    util.send_email(background_tasks, subject="Verify Your Email", recipient=[new_user.email], message=message)
    sql_query.create_otp_for_user(db=db, otp=otpdata)
    return {
        'message':'please verify your email with the one time password sent to your email'
         }


@router.post('/email-verification', status_code=status.HTTP_200_OK)
async def verify_email(otp:schema.OneTimePassword,response: Response, db:Session = Depends(get_db)):
    #get the user_id with the otp
    user_otp_qs=db.query(models.UserOneTimePassword).filter(models.UserOneTimePassword.code == otp.code)
    #check if the otp is still valid
    isValid=util.verify_otp(otp.code)
    print(isValid)
    if isValid:
        user_otp=user_otp_qs.first()
        user_qs=db.query(models.User).filter(models.User.id == user_otp.user_id)
        user=sql_query.get_user_by_id(db, user_otp.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid user")
        
        user_qs.update({"is_verified": True}, synchronize_session=False)
        user_otp_qs.update({'is_valid':False}, synchronize_session=False)
        db.commit()
        return {
            'is_verified':user.is_verified
            }
    else:
        user_otp_qs.update({'is_valid':False}, synchronize_session=False)
        response.status_code=status.HTTP_400_BAD_REQUEST
        return {
            "message":'otp has expired please try again with another otp'
        }
    




@router.post('/login', status_code=status.HTTP_200_OK)
async def login(credentials:OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    user=sql_query.check_user_exist(db, email=credentials.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"invalid credentials")
    if not util.verify_password(credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid credentials")
    
    access_token=jwt_auth.create_access_token(data={"user_id":user.id, "email":user.email})

    return {
        "access_token":access_token,
        "token_type":"bearer"
    }

@router.post('/forgot-password', status_code=status.HTTP_200_OK)
async def reset_password_request(req:schema.ForgetPasswordRequest, background_tasks:BackgroundTasks, db:Session = Depends(get_db)):
    user=sql_query.check_user_exist(db, email=req.email)
    if not user:
        return Response(content='an email to reset your password has be sent', status_code=status.HTTP_404_NOT_FOUND)
    #generate a reset token
    token=jwt_auth.create_access_token(data={'user_id':user.id})
    #sending Email
    subject="Password Reset Request"
    recipient=[user.email]
    message="""  
       <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
        </head>
        <body>
            <div style="width: 100%; font-size: 16px; margin-top: 20px; text-align: center;">
                <h1>Reset your Password</h1>
                <p>someone has request a password reset with your email {0:}, if that is you, you can reset your password with link below
                    <a href="http://127.0.0.1:8000/api/v1/reset-password?reset-token={1:}" style="margin: 10px; font-size: 16px;">Reset Password</a>
                </p>
                <p>if you didn't request this you can ignore this email</p>
                <p>your password won't change until you access the link above.</p>
            </div>
        </body>
        </html>  
    """.format(user.email, token)

    util.send_email(background_tasks, subject, recipient, message )

    return {
        'message':"email to reset your password has be sent",
    }

@router.post('/reset-password', status_code=status.HTTP_200_OK)
async def reset_password(reqBody:schema.ResetPassword, db:Session = Depends(get_db)):
    #decode the token and get the user id
    try:
        res=jwt_auth.decode_general_token(reqBody.token)

        #get the user with the id
        user_qs=db.query(models.User).filter(models.User.id == res.id)
        if not user_qs.first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        if reqBody.password != reqBody.comfirm_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="password do not match")
        #update the password
        password=util.hash_password(reqBody.password)
        user_qs.update({'password': password}, synchronize_session=False)
        db.commit()
        #return a success message when done
        return {
            "message":"password reset successfully"
        }
    except JWTError:
        return{
            "message": "token has expired or is invalid"
        }

