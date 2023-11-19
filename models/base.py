from typing import Optional
from fastapi import APIRouter, HTTPException
from sqlmodel import Field, SQLModel, select
from starlette import status

from database.db import db_dependency
from utils.hash import Hash


class BaseDataModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)

    # ? ROUTER CLASSMETHOD
    @classmethod
    def make_router(cls):
        router = APIRouter()

        # ? GET ENDPOINTS

        @router.get(
            f"/{cls.__name__.lower()}",
            status_code=status.HTTP_200_OK,
            tags=[f"{cls.__name__}"],
            summary=f"Get All - Mostrar la información de todos los {cls.__name__}",
            description=f"""
            Endpoint para mostrar la información de todos los {cls.__name__}\n
            - Base de Datos: Obligatorio
            """,
        )
        def get_all(db: db_dependency):
            return cls.get_all(db)

        @router.get(
            f"/{cls.__name__.lower()}/{{id}}",
            status_code=status.HTTP_200_OK,
            tags=[f"{cls.__name__}"],
            summary=f"Get One By ID - Mostrar la información de un {cls.__name__}",
            description=f"""
            Endpoint para mostrar la información de un {cls.__name__}\n
            - Base de Datos: Obligatorio
            - ID: Obligatorio
            """,
        )
        def get_one_by_id(id: int, db: db_dependency):
            return cls.get_one_by_id(id, db)

        # ? POST ENDPOINTS

        @router.post(
            f"/{cls.__name__.lower()}",
            status_code=status.HTTP_201_CREATED,
            tags=[f"{cls.__name__}"],
            summary=f"Create {cls.__name__} - Crear un nuevo {cls.__name__}",
            description=f"""
            Endpoint para crear un nuevo {cls.__name__}\n
            - Base de Datos: Obligatorio
            - {cls.__name__}: Obligatorio
            """,
        )
        def create_new(record: cls, db: db_dependency):
            if cls.__name__ == "User":
                statement = select(cls).where(cls.email == record.email)

                email_search = db.exec(statement).first()

                statement = select(cls).where(cls.document_id == record.document_id)

                document_id_search = db.exec(statement).first()

                if email_search or document_id_search:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Ya hay un registro con esa identificación o Email en la base de datos.",
                    )

                record.hash_password = Hash.bcrypt(record.hash_password)

            return cls.insert_new(record, db)

        # ? PUT ENDPOINTS

        @router.put(
            f"/{cls.__name__.lower()}/{{id}}",
            status_code=status.HTTP_200_OK,
            tags=[f"{cls.__name__}"],
            summary=f"Update {cls.__name__} by ID - Actualizar un {cls.__name__} por ID",
            description=f"""
            Endpoint para Actualizar un {cls.__name__}\n
            - Base de Datos: Obligatorio
            -ID: Obligatorio
            - {cls.__name__}: Obligatorio
            """,
        )
        def update_one_by_id(id: int, record: cls, db: db_dependency):
            return cls.update_one_by_id(id, record, db)

        # ? DELETE ENDPOINTS

        @router.delete(
            f"/{cls.__name__.lower()}/{{id}}",
            status_code=status.HTTP_204_NO_CONTENT,
            tags=[f"{cls.__name__}"],
            summary=f"Delete {cls.__name__} by ID - Eliminar un {cls.__name__} por ID",
            description=f"""
            Endpoint para Eliminar un {cls.__name__}\n
            - Base de Datos: Obligatorio
            -ID: Obligatorio
            """,
        )
        def delete_one_by_id(id: int, db: db_dependency):
            return cls.delete_one_by_id(id, db)

        return router

    # ? GET CLASSMETHOD

    @classmethod
    def get_all(cls, db: db_dependency):
        result = db.exec(select(cls)).all()
        if len(result) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No hay {cls.__name__}s en la Base de Datos",
            )
        return result

    @classmethod
    def get_one_by_id(cls, id: int, db: db_dependency):
        result = db.get(cls, id)

        if result == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No fue encontrado un {cls.__name__} con el ID {id} en la base de datos",
            )
        return result

    # ? POST CLASSMETHOD

    @classmethod
    def insert_new(cls, record, db: db_dependency):
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    # ? PUT CLASSMETHOD

    @classmethod
    def update_one_by_id(cls, id: int, record, db: db_dependency):
        result = db.get(cls, id)

        if result == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No fue encontrado un {cls.__name__} con el ID {id} en la base de datos",
            )
        record_data = record.dict(exclude_unset=True)

        for key, value in record_data.items():
            setattr(result, key, value)

        db.add(result)
        db.commit()
        db.refresh(result)
        return result

    # ? DELETE CLASSMETHOD

    @classmethod
    def delete_one_by_id(cls, id: int, db: db_dependency):
        result = db.get(cls, id)

        if result == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No fue encontrado un {cls.__name__} con el ID {id} en la base de datos",
            )
        db.delete(result)
        db.commit()
