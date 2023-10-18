import requests
import os


class MovieDB:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3/"

    def get_movie_details(self, movie_id):
        endpoint = f"/movie/{movie_id}"
        params = {"api_key": self.api_key}

        response = requests.get(self.base_url + endpoint, params=params)
        data = response.json()

        return data

    def search_movie(self, query):
        endpoint = "/search/movie"
        params = {"api_key": self.api_key, "query": query}

        response = requests.get(self.base_url + endpoint, params=params)
        data = response.json()

        return data.get("results", [])

    def get_movie_credits(self, movie_id):
        endpoint = f"/movie/{movie_id}/credits"
        params = {"api_key": self.api_key}

        response = requests.get(self.base_url + endpoint, params=params)
        data = response.json()

        return data

    def get_movie_video(self, movie_id):
        endpoint = f"/movie/{movie_id}/videos"
        params = {"api_key": self.api_key}

        response = requests.get(self.base_url + endpoint, params=params)
        data = response.json()

        return data

    def get_movie_image(self, movie_id):
        endpoint = f"/movie/{movie_id}/images"
        params = {"api_key": self.api_key}

        response = requests.get(self.base_url + endpoint, params=params)
        data = response.json()

        return data

    def get_movie_tag(self, movie_id):
        endpoint = f"/movie/{movie_id}"
        params = {"api_key": self.api_key}

        response = requests.get(self.base_url + endpoint, params=params)
        data = response.json()

        return data

    def extract_director_from_credits(self, credits_info):
        director = ""
        if "crew" in credits_info:
            crew = credits_info["crew"]
            directors = [
                crew_member["name"]
                for crew_member in crew
                if crew_member["job"] == "Director"
            ]
            director = directors[0] if directors else ""

        return director

    def extract_movie_details(self, movie_info, credits_info):
        movid = movie_info.get("id")
        title = movie_info.get("title", "")
        release_date = movie_info.get("release_date", "")
        overview = movie_info.get("overview")
        director = self.extract_director_from_credits(credits_info)
        year = release_date.split("-")[0] if release_date else "N/A"
        genres = movie_info.get("genres", [])
        tag = [genre["name"] for genre in genres]

        movie_details = {
            "ID": movid,
            "name": title,
            "director": director,
            "year": year,
            "overview": overview,
            "tag": " ".join(tag),
        }

        return movie_details

    def search_and_return_movie_details(self, query):
        movie_list = []

        search_results = self.search_movie(query)

        for result in search_results:
            movie_id = result["id"]

            credits_info = self.get_movie_credits(movie_id)
            movie_details = self.extract_movie_details(result, credits_info)

            video_info = self.get_movie_video(movie_id)
            video_key = (
                video_info["results"][0]["key"] if video_info.get("results") else "N/A"
            )
            movie_details["YouTube_Link"] = f"https://www.youtube.com/embed/{video_key}"

            image_info = self.get_movie_image(movie_id)
            image_key = (
                image_info["backdrops"][0]["file_path"]
                if image_info.get("backdrops")
                else "N/A"
            )
            movie_details["image_Link"] = f"http://image.tmdb.org/t/p/w500/{image_key}"

            tag_info = self.get_movie_tag(movie_id)
            tag_key1 = tag_info["genres"][0]["name"] if tag_info.get("genres") else ""
            tag_key2 = (
                tag_info["genres"][1]["name"]
                if tag_info.get("genres") and len(tag_info["genres"]) > 1
                else ""
            )

            movie_details["tag"] = f"{tag_key1} {tag_key2}"

            movie_list.append(movie_details)
        sorted_movies = sorted(
            movie_list,
            key=lambda movie_details: movie_details["year"],
            reverse=True,
        )

        return sorted_movies

    def search_and_return_movie_details_by_id(self, movie_id):
        movie_list = []

        # Fetch details of the selected movie using the MovieDB class
        result = self.get_movie_details(movie_id)
        credits_info = self.get_movie_credits(movie_id)
        movie_details = self.extract_movie_details(result, credits_info)

        video_info = self.get_movie_video(movie_id)
        video_key = (
            video_info["results"][0]["key"] if video_info.get("results") else "N/A"
        )
        movie_details["YouTube_Link"] = f"https://www.youtube.com/embed/{video_key}"

        image_info = self.get_movie_image(movie_id)
        image_key = (
            image_info["backdrops"][0]["file_path"]
            if image_info.get("backdrops")
            else "N/A"
        )
        movie_details["image_Link"] = f"http://image.tmdb.org/t/p/w500/{image_key}"

        tag_info = self.get_movie_tag(movie_id)
        tag_key1 = tag_info["genres"][0]["name"] if tag_info.get("genres") else ""
        tag_key2 = (
            tag_info["genres"][1]["name"]
            if tag_info.get("genres") and len(tag_info["genres"]) > 1
            else ""
        )

        movie_details["tag"] = f"{tag_key1} {tag_key2}"

        movie_list.append(movie_details)

        sorted_movies = sorted(
            movie_list,
            key=lambda movie_details: movie_details["year"],
            reverse=True,
        )

        return sorted_movies


API_KEY = os.environ.get("API_KEY")
movie_db = MovieDB(API_KEY)
