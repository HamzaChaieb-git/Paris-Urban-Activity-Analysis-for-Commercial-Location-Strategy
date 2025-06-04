# Transform/transform.py

def transform_all_datasets(data):
    """
    data : dict clef -> liste de records bruts (JSON “records” issus de l’API)
    Retourne : dict clef -> liste de dictionnaires contenant uniquement les champs utiles,
    avec lat/lon ou géométrie, selon chaque dataset
    """
    cleaned = {}

    for key, records in data.items():
        out = []
        for rec in records:
            f = rec.get("fields", {})
            row = {"recordid": rec.get("recordid")}

            if key == "panels":
                # Champs exacts pour “Panneaux d’Affichage Associatifs”
                row["arrondissement"] = f.get("arrondissement")
                row["adresse"] = f.get("adresse")
                row["format"] = f.get("format")
                row["gratuit"] = f.get("gratuit")
                row["type"] = f.get("type")
                if "geo_point_2d" in f:
                    row["lat"] = f["geo_point_2d"][0]
                    row["lon"] = f["geo_point_2d"][1]
                if "geo_shape" in f:
                    row["geo_shape"] = f["geo_shape"]

            elif key == "bike_counters":
                # Champs exacts pour “Comptage Vélo – Données Compteurs”
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
                # Champs exacts pour “Commerces – Eau de Paris”
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
                # Champs exacts pour “Événements – Que Faire à Paris ?”
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
                    row["lat"] = f["lat_lon"][0]
                    row["lon"] = f["lat_lon"][1]
                # Certains enregistrements ont aussi 'geo_point_2d'
                if "geo_point_2d" in f:
                    row["lat"] = f["geo_point_2d"][0]
                    row["lon"] = f["geo_point_2d"][1]

            elif key == "zti":
                # Champs exacts pour “Zones Touristiques Internationales (ZTI)”
                row["nom_zone"] = f.get("nom_zone")
                row["type_zone"] = f.get("type_zone")
                if "zone_geom" in f:
                    row["zone_geom"] = f["zone_geom"]

            out.append(row)

        print(f"🧹 Transformé {len(out)} enregistrements pour '{key}'")
        cleaned[key] = out

    return cleaned
