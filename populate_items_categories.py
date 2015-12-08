# coding=utf-8
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import Category, Base, Item, User

engine = create_engine('sqlite:///itemcatalogwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

category1 = Category(name="Men Wear",description="This category contains the\
 latest offers and designs for mens wear. All the men variety is available.\
  Order online or head to stores.", user_id=1)

session.add(category1)
session.commit()

item1 = Item(name="Cali Republic Graphic T", description="Get into a \
golden state of mind with a lil' help from our Cali Republic Graphic T! This \
cool, contemporary tee has West Coast swag for days thanks to bold \
\"California Republic\" text and a bear silhouette filled with vivid \
tropical scenery.", price="$17.50",
image_src="http://www.aeropostale.com/graphics/product_images/pAERO1-23071193t386x450.jpg",  # noqa
category=category1, user_id=1)
session.add(item1)
session.commit()

item2 = Item(name="Friday Night Graphic T", description="Throw on our Friday \
Night Graphic T and let loose 'cause you can always blame it on the weekend \
later! This fly shirt reps your bold attitude \
with \"Friday night made me do it\" text stacked on the front. Pair it with \
color-wash skinnies to stay stylish while you try not to think about Monday.",
price="$8.00", image_src="http://www.aeropostale.com/graphics/product_images/pAERO1-22133878t386x450.jpg",  # noqa
category=category1, user_id=1)
session.add(item2)
session.commit()

item3 = Item(name="Golden Bear Graphic T", description="Trendsetters, take \
note: Our Golden Bear Graphic T supplies fly style from sea to shining sea. \
You'll definitely wanna get your paws on this sharp shirt; it's designed with \
monochromatic bear and map imagery, as well as \
fuzzy \"California Golden State\" text.",
price="$12.95", image_src="http://www.aeropostale.com/graphics/product_images/pAERO1-22133829t386x450.jpg",  # noqa
category=category1, user_id=1)
session.add(item3)
session.commit()

item4 = Item(name="A87 Tipped Logo Pique Polo", description="TPull your \
first-date getup together in a snap with our A87 Tipped Logo Pique Polo and \
chinos. This classic shirt is designed with traditional ribbing, pearlized \
buttons and vented hems, while contrast trim and \"A87\" embroidery add cool \
accents that your girl is sure to love.",
price="$22.00", image_src="http://www.aeropostale.com/graphics/product_images/pAERO1-21748990t386x450.jpg",  # noqa
category=category1, user_id=1)
session.add(item4)
session.commit()

item5 = Item(name="Aeropostale New York Full-Zip", description="Before you \
embark on your chilly-day excursions, layer up with warm pieces like our \
Aeropostale New York Full-Zip Hoodie! It features a soft fleecy construction \
and two pouch pockets, while printed signature text adds preppy charm.",
price="$32.00", image_src="http://www.aeropostale.com/graphics/product_images/pAERO1-21748990t386x450.jpg",  # noqa
category=category1, user_id=1)
session.add(item5)
session.commit()

category2 = Category(name="Women Wear",description="This category contains the\
 latest offers and designs for women wear. All the men variety is available.\
  Order online or head to stores.", user_id=1)

session.add(category2)
session.commit()

item1 = Item(name="Roundneck T Shirt", description="Latest roundneck t shirt\
 to make you look cool. Built with 100% cotton. \
 Rest of the text is just a space filling\
  text to make it look like a long paragraph with complete description. \
  Although, there is nothing important here but still have spend time to write \
  this text. Hopefully this is enough.",
                     price="$17.50", category=category2, user_id=1)
session.add(item1)
session.commit()

item2 = Item(name="Jeans", description="Latest pair of jeans\
 to make you look cool. Built with 100&amp; cotton. Rest of the text is just \
 a space filling\
  text to make it look like a long paragraph with complete description. \
  Although, there is nothing important here but still have spend time to write \
  this text. Hopefully this is enough.",
                     price="$8.00", category=category2, user_id=1)
session.add(item2)
session.commit()

item3 = Item(name="Slim fit shirt", description="Hand woven shirt\
 to make you look trendy and casual. Rest of the text is just a space filling\
  text to make it look like a long paragraph with complete description. \
  Although, there is nothing important here but still have spend time to write \
  this text. Hopefully this is enough.",
                     price="$12.95", category=category2, user_id=1)
session.add(item3)
session.commit()

category3 = Category(name="Kids Wear",description="This category contains the\
 latest offers and designs for Kids wear. All the men variety is available.\
  Order online or head to stores.", user_id=1)

session.add(category3)
session.commit()

item2 = Item(name="Jeans", description="Latest pair of jeans\
 to make you look cool. Built with 100&amp; cotton. Rest of the text is just \
 a space filling\
  text to make it look like a long paragraph with complete description. \
  Although, there is nothing important here but still have spend time to write \
  this text. Hopefully this is enough.",
                     price="$8.00", category=category3, user_id=1)
session.add(item2)
session.commit()

item3 = Item(name="Slim fit shirt", description="Hand woven shirt\
 to make you look trendy and casual. Rest of the text is just a space filling\
  text to make it look like a long paragraph with complete description. \
  Although, there is nothing important here but still have spend time to write \
  this text. Hopefully this is enough.",
                     price="$12.95", category=category3, user_id=1)
session.add(item3)
session.commit()

print "database has been populated!"
