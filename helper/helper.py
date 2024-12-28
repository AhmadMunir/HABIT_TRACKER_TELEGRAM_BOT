from models.user import User

def update_stage(session, id_telegram, stage):
    user = session.query(User).filter(User.id_telegram == id_telegram).first()
    user.stage = stage
    session.commit()
    return user