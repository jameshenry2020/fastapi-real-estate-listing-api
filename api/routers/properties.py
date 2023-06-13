from cloudinary.uploader import upload
from fastapi import APIRouter, Body, Form, Query, status, Response, Depends, HTTPException, File, UploadFile
from .. import schema, sql_query,  jwt_auth, models
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List, Union

router=APIRouter(
    prefix="/api/v1/properties",
    tags=['Properties']
)

@router.post('/', status_code=status.HTTP_201_CREATED)
async def add_property(reqbody:schema.PropertyBase =  Body(...), file:UploadFile = File(...),  db:Session = Depends(get_db), current_user: int = Depends(jwt_auth.get_authenticate_user)):
    agent=db.query(models.AgentDetails).filter(models.AgentDetails.user_id == current_user.id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you are not an agent")
    result = upload(file.file, public_id=f"agent_properties")
    url=result.get('url')
    new_property=sql_query.create_new_property(db, property=reqbody, imgurl=url, agent_id=agent.id)
    return new_property

@router.post('/upload_property_image', status_code=status.HTTP_201_CREATED, response_model=schema.PropertyImageOut)
async def add_property_image(property_id:int = Form(...), file: UploadFile = File(...), db:Session = Depends(get_db), current_user:int = Depends(jwt_auth.get_authenticate_user)):
    agent=db.query(models.AgentDetails).filter(models.AgentDetails.user_id == current_user.id).first()
    property=db.query(models.Property).filter(models.Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="property with this id does not exist")
    if property.agent_id != agent.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you are not authorized to upload this image")
    image = upload(file.file, public_id="property_image")
    url=image.get('url')
    return sql_query.add_image_to_property(db, property_id=property.id, imgUrl=url)


#get the list of all properties
@router.get('/', status_code=status.HTTP_200_OK, response_model=List[schema.Property])
async def get_properties(
    title:Union[str, None] = Query(default=None), 
    country:Union[str, None] = Query(default=None),
    location:Union[str, None] = Query(default=None),
    db:Session= Depends(get_db)):
    all_properties_qs=db.query(models.Property)
    all_properties=all_properties_qs.all()
    if title | country | location:
       all_properties=all_properties_qs.filter(models.Property.title == title).filter(models.Property.country == country).filter(models.Property.city == location).all()
    return all_properties

#get list of properties by an agent
@router.get('/agent_properties', status_code=status.HTTP_200_OK, response_model=List[schema.Property])
async def get_agent_properties(agent_id:int, db:Session = Depends(get_db)):
    agent=db.query(models.AgentDetails).filter(models.AgentDetails.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="agent with this id does not exist")
    properties=db.query(models.Property).filter(models.Property.agent_id == agent_id).all()
    return properties

#get a single property
@router.get('/{property_id}', status_code=status.HTTP_200_OK, response_model=schema.Property)
async def get_property(property_id:int, db:Session = Depends(get_db)):
    property=db.query(models.Property).filter(models.Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"property with the id {id} does not exist")
    return property

#agent to update property details
@router.patch('/{property_id}', status_code=status.HTTP_200_OK)
def update_property(property_id: int, updated_data:schema.PropertyBase, db: Session = Depends(get_db), current_user: int = Depends(jwt_auth.get_authenticate_user)):
    agent=db.query(models.AgentDetails).filter(models.AgentDetails.user_id == current_user.id).first()
    property_qs=db.query(models.Property).filter(models.Property.id == id)
    property=property_qs.first()
    if property is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"property with the id {property_id} does not exist")
    if property.agent_id != agent.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"you are not authorised to update this property")
    property_qs.update(updated_data.dict(), synchronize_session=False)
    db.commit()
    return property_qs.first()

@router.delete('/{property_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_note(property_id: int, db:Session = Depends(get_db), current_user: int = Depends(jwt_auth.get_authenticate_user)):
    agent=db.query(models.AgentDetails).filter(models.AgentDetails.user_id == current_user.id).first()
    property_qs=db.query(models.Property).filter(models.Property.id == property_id)
    property=property_qs.first()
    if property is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"note with the id {property_id} does not exist")
    if property.agent_id != agent.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"you are not authorised to delete this note")
    property_qs.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)