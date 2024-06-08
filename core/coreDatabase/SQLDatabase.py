from typing import Any, Dict
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, MetaData, Table,UniqueConstraint , JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import IntegrityError

from core.coreDatabase.IDatabase import Database

Base = declarative_base()

class SQLAlchemyDatabase(Database):
    
    def initialize(self):
        self.connect()
        self.define_table()
        
   
    def connect(self):
        try:
            self.engine = create_engine(self.connection_info)
            self.metadata = MetaData()
            self.session = sessionmaker(bind=self.engine)()
            self.logger.info("Database connection established.")
        except Exception as e:
            self.logger.error(f"Failed to connect to the database: {e}")
            raise


    def define_table(self):
        try:
            columns = [Column('id', Integer, primary_key=True, autoincrement=True)]
            unique_constraints = []

            for field, attrs in self.schema.items():
                col_type = getattr(self, f"_get_{attrs['type'].lower()}_type")()
                column_args = {}
                if "unique" in attrs:
                    column_args["unique"] = attrs["unique"]
                if "default" in attrs:
                    column_args["default"] = attrs["default"]
                columns.append(Column(field, col_type, **column_args))
                if attrs.get("unique"):
                    unique_constraints.append(field)
            
            self.table = Table(self.table_name, self.metadata, *columns)

            if unique_constraints:
                self.table.append_constraint(UniqueConstraint(*unique_constraints))

            self.metadata.create_all(self.engine)
            self.logger.info(f"Table '{self.table_name}' defined successfully.")
        except Exception as e:
            self.logger.error(f"Failed to define table '{self.table_name}': {e}")
            raise


    def create(self, data: Dict[str, Any]) -> bool:
        try:
            insert_stmt = self.table.insert().values(data)
            self.session.execute(insert_stmt)
            self.session.commit()
            return True
        except IntegrityError:
            # Handle unique constraint violation without logging
            self.session.rollback()
            return False
        except Exception as e:
            self.logger.error(f"Failed to create record: {e}")
            self.session.rollback()
            return False

    def read(self, query: Dict[str, Any], limit: int = 0) -> Any:
        try:
            select_stmt = self.table.select().where(
                *(self.table.c[k] == v for k, v in query.items())
            )
            if limit > 0:
                select_stmt = select_stmt.limit(limit)
            result = self.session.execute(select_stmt).fetchall()
            self.logger.info(f"Records read successfully with query: {query}, limit: {limit}")
            return [dict(row._mapping) for row in result]
        except Exception as e:
            self.logger.error(f"Failed to read records with query: {e}")
            return []

    def update(self, query: Dict[str, Any], data: Dict[str, Any]) -> bool:
        try:
            update_stmt = self.table.update().where(
                *(self.table.c[k] == v for k, v in query.items())
            ).values(data)
            self.session.execute(update_stmt)
            self.session.commit()
            self.logger.info(f"Records updated successfully with query: {query} ")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update records with query: {e}")
            return False

    def delete(self, query: Dict[str, Any]) -> bool:
        try:
            delete_stmt = self.table.delete().where(
                *(self.table.c[k] == v for k, v in query.items())
            )
            self.session.execute(delete_stmt)
            self.session.commit()
            self.logger.info(f"Records deleted successfully with query: {query}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete records with query: {e}")
            return False

    def _get_text_type(self):
        return String

    def _get_real_type(self):
        return Float

    def _get_int_type(self):
        return Integer
    
    def _get_DICT_type(self):
        return JSON
