from sqlalchemy import create_engine, Column, String, Float, Text, Integer
from sqlalchemy.orm import declarative_base, sessionmaker, exc
import json
from sqlalchemy.sql.expression import func
from sqlalchemy.exc import SQLAlchemyError , IntegrityError, NoResultFound
from core.utils import Utils
Base = declarative_base()


class KijijiAd(Base):
    __tablename__ = 'kijiji_ads'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(Text)
    price = Column(Float)
    attributes = Column(Text)  # Storing as a JSON string key value pair
    images = Column(Text)  # Storing as a JSON string list keep it like that in csv
    url = Column(String, unique=True)
    activation_date = Column(String)
    sorting_date = Column(String)
    _processState = Column(String)
    _state = Column(String)
    address = Column(String)
    location = Column(Text)  # Storing as a JSON string dict of key val
    sellerName = Column(String)
    def __repr__(self):
        return f"<Listing(title='{self.title}', price={self.price})>"
class Database:
    
    def __init__(self, db_url='sqlite:///default.db'):
        self.logger = Utils.get_logger()  # Configuring the logger for this module
        self.db_url = db_url
        
        try:
            # Attempt to create an engine and bind a sessionmaker to it
            self.engine = create_engine(db_url, echo=False)
            Base.metadata.create_all(self.engine)  # Create all tables based on the Base metadata
            self.Session = sessionmaker(bind=self.engine)
            self.logger.info(f"Database initialized successfully with {db_url}")
        except SQLAlchemyError as e:
            # Handle specific SQLAlchemy exceptions if necessary
            self.logger.error(f"Failed to connect to the database at {db_url}: {str(e)}")
            raise Exception(f"Database initialization failed: {str(e)}")
        except Exception as e:
            # General exception handling if something else goes wrong
            self.logger.error(f"An unexpected error occurred during database initialization: {str(e)}")
            raise Exception(f"Database initialization failed: {str(e)}")

    def add_listing(self, listing_data):
        """
        Adds a new listing to the database.
        Args:
            listing_data (dict): A dictionary containing the listing data.
        Returns:
            int: 1 if the listing was added successfully, 0 otherwise.
        """
        session = self.Session()
        try:
            # Check if the listing already exists to prevent duplicate entries
            if session.query(KijijiAd.id).filter_by(url=listing_data.get('url')).scalar() is not None:
                self.logger.info("Listing already exists with URL: %s", listing_data.get('url'))
                return 0

            # Create a new listing instance
            listing = KijijiAd(
                    id=listing_data['id'],
                    title=listing_data['title'],
                    description=listing_data['description'],
                    price=listing_data['price'],
                    attributes=json.dumps(listing_data['attributes']),
                    images=json.dumps(listing_data['images']),
                    url=listing_data['url'],
                    activation_date=listing_data['activation_date'],
                    sorting_date=listing_data['sorting_date'],
                    _processState=listing_data['_processState'],
                    _state=listing_data['_state'],
                )

            # Add to session and commit
            session.add(listing)
            session.commit()
            self.logger.info("New listing added successfully: %s", listing)
            return 1

        except IntegrityError:
            # Handle integrity issues, such as unique constraint violations
            self.logger.error("Integrity error occurred while adding a new listing.", exc_info=True)
            session.rollback()
            return 0
        except SQLAlchemyError as e:
            # Handle other SQLAlchemy errors
            self.logger.error("Database error occurred: %s", str(e), exc_info=True)
            session.rollback()
            return 0
        except Exception as e:
            # Handle unexpected errors
            self.logger.error("Unexpected error occurred: %s", str(e), exc_info=True)
            session.rollback()
            return 0
        finally:
            # Ensure that the session is closed in any case
            session.close()    
      
    def update_listing(self, id, updated_data):
        """
        Updates an existing listing in the database with new data.

        Args:
            id (int): The ID of the listing to update.
            updated_data (dict): A dictionary of fields to update.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        session = self.Session()
        try:
            # Fetch the listing by ID
            listing = session.query(KijijiAd).filter(KijijiAd.id == id).one()
            # Update fields
            for key, value in updated_data.items():
                if hasattr(listing, key):
                    # Properly handle JSON serialization for specific fields
                    serialized_value = json.dumps(value, ensure_ascii=False) if key in ['attributes', 'images', 'location'] else value
                    setattr(listing, key, serialized_value)
            session.commit()
            self.logger.info(f"Listing {id} updated successfully.")
            return True
        except NoResultFound:
            # Log and handle the case where no listing is found
            self.logger.warning(f"No listing found with ID {id}.")
            session.rollback()
            return False
        except SQLAlchemyError as e:
            # Handle general SQLAlchemy errors
            self.logger.error(f"Database error while updating listing {id}: {str(e)}", exc_info=True)
            session.rollback()
            return False
        except Exception as e:
            # Catch-all for any other unexpected errors
            self.logger.error(f"Unexpected error while updating listing {id}: {str(e)}", exc_info=True)
            session.rollback()
            return False
        finally:
            # Always ensure the session is closed
            session.close()

    def get_all_ads(self):
        """
        Retrieves all advertisements from the database.

        Returns:
            list: A list of KijijiAd instances or an empty list if no ads are found or an error occurs.
        """
        session = self.Session()
        try:
            listings = session.query(KijijiAd).all()
            if listings:
                self.logger.info(f"Successfully retrieved {len(listings)} ads from the database.")
            else:
                self.logger.info("No ads found in the database.")
            return listings
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to retrieve ads from the database: {str(e)}", exc_info=True)
            return []  # Return an empty list in case of error
        finally:
            session.close()

    def fetch_random_new_ad(self):
        """
        Fetches a random advertisement that is marked as 'NEW' from the database.

        Returns:
            KijijiAd: An instance of KijijiAd that is in 'NEW' state or None if no such ad exists.
        """
        session = self.Session()
        try:
            random_ad = session.query(KijijiAd)\
                               .filter_by(_processState='NEW')\
                               .order_by(func.random())\
                               .first()
            if random_ad:
                self.logger.info(f"Random new ad fetched successfully: {random_ad.id}")
            else:
                self.logger.info("No new ads available to fetch.")
            return random_ad
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to fetch a random new ad due to a database error: {str(e)}", exc_info=True)
            return None
        finally:
            session.close()

    def get_sample_ad_with_columns(self):
        session = self.Session()
        sample_ad = session.query(KijijiAd).order_by(func.random()).first()
        session.close()
        if sample_ad:
            # Extracting column names
            column_names = KijijiAd.__table__.columns.keys()
            # Extracting a sample ad data
            sample_data = {column: getattr(sample_ad, column) for column in column_names}
            return column_names, sample_data
        else:
            return None, None

    def get_ads(self, limit=None, **filters):
        """
        Fetches advertisements from the database with optional filtering and limiting.

        Args:
            limit (int, optional): Maximum number of ads to return.
            **filters (dict): Arbitrary number of filters by column names and values. Special handling for JSON-encoded 'attributes'.

        Returns:
            list: A list of filtered KijijiAd instances or an empty list if no ads match.
        """
        with self.Session() as session:
            try:
                query = session.query(KijijiAd)
                
                # Apply filters for normal columns dynamically
                for attr, value in filters.items():
                    if attr != 'attributes':
                        query = query.filter(getattr(KijijiAd, attr) == value)
                
                # First fetch all results filtered without JSON attributes
                results = query.all()
                    
    # Special handling for 'attributes' if provided in filters
                if 'attributes' in filters:
                    attributes_filter = filters['attributes']
                    filtered_results = []
                    for ad in results:
                        # Parse the JSON string from the 'attributes' column
                        try:
                            ad_attributes = json.loads(ad.attributes) if ad.attributes else {}
                            self.logger.debug(f"Parsed attributes for ad ID {ad.id}: {ad_attributes}")
                            
                            # Check if all key-value pairs in attributes_filter match those in ad_attributes
                            match = all(
                                ad_attributes.get(key) == value
                                for key, value in attributes_filter.items()
                            )
                            if match:
                                filtered_results.append(ad)
                            
                        except json.JSONDecodeError as e:
                            self.logger.error(f"JSON decoding error for ad ID {ad.id}: {str(e)}")
                    results = filtered_results
                    
                # Apply limit if specified
                if limit is not None:
                    results = results[:limit]

                self.logger.info(f"Retrieved {len(results)} ads with specified filters.")
                return results
            except SQLAlchemyError as e:
                self.logger.error(f"Failed to retrieve ads from the database: {str(e)}", exc_info=True)
                return []
