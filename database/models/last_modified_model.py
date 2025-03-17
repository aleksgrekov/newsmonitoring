from sqlalchemy.orm import Mapped

from models.base_model import Base


class LastModified(Base):
    __tablename__ = "last_modified"

    last_modified: Mapped[str]

    def __repr__(self):
        return f"<LastModifiedModel(id={self.id}, last_modified={self.last_modified})>"
