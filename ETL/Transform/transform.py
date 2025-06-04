# Transform/transform.py

def transform_all_datasets(raw_data):
    """
    raw_data: dict (key -> list of API “record” objects)
    Returns: dict (key -> list of cleaned dicts with only needed fields)
    """
    cleaned = {}

    for key, records in raw_data.items():
        out = []
        for rec in records:
            f = rec.get("fields", {})
            row = {"recordid": rec.get("recordid")}

            if key == "panels":
                # Fields: arrondissement, adresse, format, gratuit, type, geo_point_2d, geo_shape
                row["arrondissement"] = f.get("arrondissement")
                row["adresse"]       = f.get("adresse")
                row["format"]        = f.get("format")
                row["gratuit"]       = f.get("gratuit")
                row["type"]          = f.get("type")
                if "geo_point_2d" in f:
                    row["lat"] = f["geo_point_2d"][0]
                    row["lon"] = f["geo_point_2d"][1]
                if "geo_shape" in f:
                    row["geo_shape"] = f["geo_shape"]

            elif key == "bike_counters":
                # Fields: id_compteur, nom_compteur, id_site, nom_site, comptage,
                #         date, heure, date_install, photo_lien, geo_point_2d, geo_shape
                row["id_compteur"]   = f.get("id_compteur")
                row["nom_compteur"]  = f.get("nom_compteur")
                row["id_site"]       = f.get("id_site")
                row["nom_site"]      = f.get("nom_site")
                row["comptage"]      = f.get("comptage")
                row["date"]          = f.get("date")
                row["heure"]         = f.get("heure")
                row["date_install"]  = f.get("date_install")
                row["photo_lien"]    = f.get("photo_lien")
                if "geo_point_2d" in f:
                    row["lat"] = f["geo_point_2d"][0]
                    row["lon"] = f["geo_point_2d"][1]
                if "geo_shape" in f:
                    row["geo_shape"] = f["geo_shape"]

            elif key == "commerces":
                # Fields: nom_du_commerce, adresse, type_de_distribution, horaires,
                #         contact, geo_point_2d, geo_shape
                row["nom_du_commerce"]      = f.get("nom_du_commerce")
                row["adresse"]              = f.get("adresse")
                row["type_de_distribution"] = f.get("type_de_distribution")
                row["horaires"]             = f.get("horaires")
                row["contact"]              = f.get("contact")
                if "geo_point_2d" in f:
                    row["lat"] = f["geo_point_2d"][0]
                    row["lon"] = f["geo_point_2d"][1]
                if "geo_shape" in f:
                    row["geo_shape"] = f["geo_shape"]

            elif key == "events":
                # Fields: title, description, date_start, date_end, tags, placename,
                #         address, lat_lon, price, url, geo_point_2d (sometimes)
                row["title"]       = f.get("title")
                row["description"] = f.get("description")
                row["date_start"]  = f.get("date_start")
                row["date_end"]    = f.get("date_end")
                row["tags"]        = f.get("tags")
                row["placename"]   = f.get("placename")
                row["address"]     = f.get("address")
                row["price"]       = f.get("price")
                row["url"]         = f.get("url")
                if "lat_lon" in f:
                    coords = f["lat_lon"]
                    row["lat"] = coords[0]
                    row["lon"] = coords[1]
                elif "geo_point_2d" in f:
                    row["lat"] = f["geo_point_2d"][0]
                    row["lon"] = f["geo_point_2d"][1]

            elif key == "zti":
                # Fields: nom_zone, type_zone, zone_geom
                row["nom_zone"] = f.get("nom_zone")
                row["type_zone"] = f.get("type_zone")
                if "zone_geom" in f:
                    row["zone_geom"] = f["zone_geom"]

            out.append(row)

        print(f"[Transform] Cleaned {len(out)} records for '{key}'")
        cleaned[key] = out

    return cleaned
