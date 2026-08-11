export const cities = [
  {
    name: "Delhi",
    aqi: 214,
    category: "Poor",
    accent: "#ff6b3d",
    image: "https://picsum.photos/seed/delhi-haze/1200/1600",
    copy: "A dense northern basin where winter inversions can hold pollution close to the ground.",
  },
  {
    name: "Mumbai",
    aqi: 92,
    category: "Satisfactory",
    accent: "#d6ff4b",
    image: "https://picsum.photos/seed/mumbai-coast/1200/1600",
    copy: "Coastal circulation brings relief, while traffic and construction shape local exposure.",
  },
  {
    name: "Bangalore",
    aqi: 78,
    category: "Satisfactory",
    accent: "#79e5c4",
    image: "https://picsum.photos/seed/bangalore-rain/1200/1600",
    copy: "Elevation and seasonal rain help dispersion across a fast-growing urban landscape.",
  },
  {
    name: "Chennai",
    aqi: 104,
    category: "Moderate",
    accent: "#ffd166",
    image: "https://picsum.photos/seed/chennai-coast/1200/1600",
    copy: "Sea breeze cycles and industrial corridors create a distinct daily air pattern.",
  },
  {
    name: "Hyderabad",
    aqi: 119,
    category: "Moderate",
    accent: "#ffad66",
    image: "https://picsum.photos/seed/hyderabad-sky/1200/1600",
    copy: "Dry conditions and expanding mobility networks make particulate changes easy to miss.",
  },
];

export const modelResults = [
  { model: "Linear Regression", r2: 0.9196, mae: 14.68 },
  { model: "Ridge", r2: 0.9196, mae: 14.681 },
  { model: "Gradient Boosting", r2: 0.919, mae: 14.718 },
  { model: "LightGBM", r2: 0.9154, mae: 14.965 },
  { model: "Random Forest", r2: 0.9153, mae: 15.147 },
];

export const driftFeatures = [
  { name: "AQI yesterday", value: 0.1129, status: "Watch" },
  { name: "AQI 3-day average", value: 0.2058, status: "Alert" },
  { name: "PM2.5 yesterday", value: 0.1129, status: "Watch" },
  { name: "PM10 yesterday", value: 0.1129, status: "Watch" },
];
