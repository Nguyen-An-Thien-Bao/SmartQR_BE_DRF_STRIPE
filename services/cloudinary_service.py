import cloudinary.uploader
import cloudinary

class CloudinaryService:

    @staticmethod
    def upload_image(file, folder="menu_items"):
        try:
            result = cloudinary.uploader.upload(file)
        except Exception as e:
            raise Exception("Upload failed")
        return {
            "url": result.get("secure_url"),
            "public_id": result.get("public_id")
        }

    @staticmethod
    def delete_image(public_id):
        if public_id:
            return cloudinary.uploader.destroy(public_id)
        return None