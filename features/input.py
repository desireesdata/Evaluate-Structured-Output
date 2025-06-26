def get_text_from_file(file: str, test: bool)->str:
    """

    Args:
        file (str): nom du fichier
        test (bool): true pour afficher le contenu du fichier

    Returns:
        str: retourne le contenu du fichier 
    """
    try:
        txt = open(file, 'r')
        print("Fichier lu : ", txt, "\n")
        content = txt.read()
        if test:
            print(content)
        else :
            print("\n")
        return content
    except IOError as e:
        print("Oops y a une couille dans le fichier", txt)
        return ""
 