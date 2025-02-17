from flask import request, jsonify
import requests
from io import BytesIO
import PIL.Image
import pytesseract

# UTILS
from utils.upload_img import upload_image_to_cloudinary
from utils.generate_story import generate_story
from utils.analyze_tags import analyze_tags

# CONFIG
from config.database import db

# MODELS
from models.story import Story
from models.image import Image
from models.tags import Tags


class StoryController:
    # generate story from image
    @staticmethod
    def generate_story_from_image():
        try:
            payload = request.get_json()

            # Get user from headers authorization
            user = request.headers.get('Authorization')

            # Split the session into the bearer and the user email
            user_email = user.split(' ')[1]

             # Get user_id from email
            query = "SELECT id FROM users WHERE email = %s;"
            user_id = db.engine.execute(query, (user_email)).fetchone().id

            # Get the base64 image from the request body
            file = payload['file']

            # Get theme from the request body: themes {romance: true, horror: false, comedy: false}
            themes = payload['themes']

            # Create an array of themes where the value is true
            selected_themes = [theme for theme,
                               value in themes.items() if value]

            # Get the desc from the request body
            desc = payload['description']

            # Get the title from the request body
            title = payload['title']

            # Tags for analysis
            tags = ['happy', 'sad', 'calm', 'exciting', 'positive',
                    'negative', 'neutral', 'uplifting', 'romantic', 'mysterious']

            # Analyze the tags
            tag_analysis = analyze_tags(tags)

            # Upload the image to Cloudinary
            cloudinary_data = upload_image_to_cloudinary(file)

            # Get the secure link from cloudinary
            cloudinary_link = cloudinary_data['secure_url']

            # Extract tags from the Cloudinary metadata
            cloudinary_tags = cloudinary_data['tags']

            # Join the tags into a string
            tags_string = ','.join(cloudinary_tags)

            image_text = ""

            if not cloudinary_tags:
                return jsonify({'error': 'No Cloudinary-generated tags found'})

            # Generate a story based on the Cloudinary-generated tags
            story = generate_story(
                tags=cloudinary_tags,
                tag_analysis=tag_analysis,
                image_text=image_text,
                story_title=title,
                desc=desc,
                themes=selected_themes,
            )

            # Save the image in the "images" table
            new_image = Image(
                user_id=user_id,
                image_path=cloudinary_data['secure_url'],
            )

            try:
                db.session.add(new_image)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': str(e)}), 500

            # Retrieve the ID of the newly saved image
            image_id = new_image.id

            # Create a new Story instance and set its attributes
            new_story = Story(
                user_id=user_id,
                image_id=image_id,
                story_content=story,
                story_title=title
            )

            try:
                # Add the new story to the database
                db.session.add(new_story)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': str(e)}), 500

            # Retrieve the ID of the newly saved story
            story_id = new_story.id

            # Store tags_string in the database
            new_tags = Tags(
                story_id=story_id,
                image_id=image_id,
                tags_string=tags_string
            )

            try:
                db.session.add(new_tags)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': str(e)}), 500

            return jsonify({
                'story': story,
                'cloudinary_data': cloudinary_data
            })

        except Exception as e:
            # Handle exceptions and return an error response
            return jsonify({'error': str(e)}), 500

    # get all stories
    @staticmethod
    def get_all_stories():
        try:
            # Retrieve all stories from the database
            stories = Story.query.all()

            # Convert the stories into the format we want
            stories_list = []
            for story in stories:
                # Retrieve the associated image for each story
                image = Image.query.get(story.image_id)
                if image:
                    image_url = image.image_path
                else:
                    image_url = None

                stories_list.append({
                    'id': story.id,
                    'user_id': story.user_id,
                    'story_title': story.story_title,
                    'image_url': image_url,
                    'story_content': story.story_content,
                    'created_at': story.created_at
                })

            return jsonify({'stories': stories_list, "message": "Stories data fetched successfully"})

        except Exception as e:
            # Handle exceptions and return an error response
            return jsonify({'error': str(e)})

    # Get story by id
    @staticmethod
    def get_story(story_id):
        print("Getting story with id: ", story_id)
        try:
            # Retrieve the story from the database
            story = Story.query.get(story_id)

            # Check if the story exists
            if not story:
                return jsonify({'error': 'Story not found'})

            # Retrieve the associated image for the story
            image = Image.query.get(story.image_id)
            if image:
                image_url = image.image_path
            else:
                image_url = None

            # Retrieve the associated tags for the story as a single string
            tags_string = db.session.query(Tags.tags_string).filter(
                Tags.story_id == story_id).first()

            # Split the tags string into individual tags using comma as the delimiter
            if tags_string:
                tag_list = [tag.strip() for tag in tags_string[0].split(',')]
            else:
                tag_list = []

            # Convert the story into the format we want, including tags
            story_data = {
                'id': story.id,
                'user_id': story.user_id,
                'image_url': image_url,
                'story_content': story.story_content,
                'created_at': story.created_at,
                'tags': tag_list
            }

            return jsonify({'story': story_data})

        except Exception as e:
            # Handle exceptions and return an error response
            return jsonify({'error': str(e)})

    @staticmethod
    def get_all_story_ids():
        query = "SELECT id FROM story ORDER BY created_at DESC;"
        return db.engine.execute(query).fetchall()
