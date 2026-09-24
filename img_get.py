import os
import requests

# Map your app's trek names to their Wikipedia article titles
trek_names_map = {
    "Everest Base Camp": "Everest Base Camp",
    "Annapurna Circuit": "Annapurna Circuit",
    "Inca Trail": "Inca Trail to Machu Picchu",
    "Kilimanjaro": "Mount Kilimanjaro",
    "Tour du Mont Blanc": "Tour du Mont Blanc",
    "Patagonia W Trek": "Torres del Paine National Park",
    "Zion Narrows": "The Narrows (Zion National Park)",
    "Grand Canyon Rim": "Grand Canyon",
    "Yosemite Half Dome": "Half Dome",
    "Kalalau Trail": "Kalalau Trail",
    "Laugavegur Trail": "Laugavegur",
    "Routeburn Track": "Routeburn Track",
    "West Highland Way": "West Highland Way"
}

# Create a folder to hold the downloads
save_folder = "trek_images"
os.makedirs(save_folder, exist_ok=True)

print("Downloading real trek images from Wikipedia...")

for app_name, wiki_name in trek_names_map.items():
    safe_name = app_name.replace(" ", "_")
    filename = os.path.join(save_folder, f"{safe_name}.jpg")
    
    try:
        # Ask Wikipedia for the main page image
        url = f"https://en.wikipedia.org/w/api.php?action=query&titles={wiki_name}&prop=pageimages&format=json&pithumbsize=1000"
        headers = {'User-Agent': 'TrekkingAppDev/1.0 (Local Testing)'}
        
        response = requests.get(url, headers=headers).json()
        pages = response['query']['pages']
        page = list(pages.values())[0]
        
        if 'thumbnail' in page:
            img_url = page['thumbnail']['source']
            # Download the actual image file
            img_data = requests.get(img_url, headers=headers).content
            with open(filename, 'wb') as handler:
                handler.write(img_data)
            print(f"✅ Downloaded: {app_name}")
        else:
            print(f"⚠️ No image found for: {app_name}")
            
    except Exception as e:
        print(f"❌ Failed to download {app_name}: {e}")

print(f"\nAll done! Check the '{save_folder}' folder.")