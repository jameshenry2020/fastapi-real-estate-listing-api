from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from fastapi import APIRouter,  status, Depends, HTTPException, File, UploadFile
from .. import schema, sql_query,  jwt_auth, models
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List

router=APIRouter(
    prefix="/api/v1/agent",
    tags=['Agents']
)

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schema.Agent)
async def add_agent_details(agent:schema.AgentCreate, db:Session=Depends(get_db), current_user: int = Depends(jwt_auth.get_authenticate_user)):
    #check if user already has agent account
    user_agent=db.query(models.AgentDetails).filter(models.AgentDetails.user_id==current_user.id).first()
    if user_agent:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="authenticated user is already an agent")
    new_agent=models.AgentDetails(user_id=current_user.id,  **agent.dict())
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    return new_agent



@router.post('/upload-agent-photo', status_code=status.HTTP_200_OK, response_model=schema.Agent)
async def upload_profile_image(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: int = Depends(jwt_auth.get_authenticate_user)):
    user_id=current_user.id
    #retrieve login in agents
    agent_qs=db.query(models.AgentDetails).filter(models.AgentDetails.user_id == user_id)
    if not agent_qs.first():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you are not registered as an agent")
    result = upload(file.file, public_id="agent_profile")
    url, options = cloudinary_url("agent_profile", width=100, height=150, crop="fill")
    img_url = result.get("url")
    print(img_url)
    print(url)
    agent_qs.update({'profile_img':img_url}, synchronize_session=False)
    db.commit()
    return agent_qs.first()
    

    


@router.get('/{agent_id}', status_code=status.HTTP_200_OK, response_model=schema.Agent)
async def get_agent_profile(agent_id:int, db:Session=Depends(get_db)):
    agent = sql_query.get_agent_by_id(db, agent_id=agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"agent with the id {agent_id} does not exist")
    return agent


@router.get('/', status_code=status.HTTP_200_OK, response_model=List[schema.Agent])
async def get_agent_list(db:Session=Depends(get_db)):
    agents=sql_query.get_all_agents(db=db)
    return agents