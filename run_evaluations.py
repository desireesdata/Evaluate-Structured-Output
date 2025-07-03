#!/usr/bin/env python3
import os
import subprocess
import glob
import argparse
import sys

def run_evaluation_command(gt_file, predictions_pattern, output_dir, distance_method):
    """Run the evaluation command for a specific ground truth and predictions pattern"""
    cmd = [
        "python", "main.py",
        "-i", gt_file, predictions_pattern,
        "-o", output_dir,
        "-d", distance_method
    ]
    
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Success: {output_dir}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False

def setup_argument_parser():
    """Configure et retourne le parser d'arguments"""
    parser = argparse.ArgumentParser(description='ESO - Evaluation par lots avec mapping automatique GT/prédictions')
    parser.add_argument('-p', '--predictions-dir', required=True,
                       help='Dossier contenant les fichiers de prédictions')
    parser.add_argument('-g', '--gt-dir', default='gt',
                       help='Dossier contenant les fichiers de vérité terrain (défaut: gt)')
    parser.add_argument('-o', '--output-dir', required=True,
                       help='Dossier de sortie pour les évaluations')
    parser.add_argument('-d', '--distance', choices=['levenshtein', 'ratcliff'], 
                       default='ratcliff', help='Méthode de calcul de distance')
    parser.add_argument('--pages', nargs='+', 
                       help='Pages spécifiques à traiter (ex: page_02 page_03)')
    return parser

def discover_page_mappings(predictions_dir, gt_dir):
    """Découvre automatiquement les mappings entre pages et fichiers GT"""
    page_mappings = {}
    
    # Chercher tous les fichiers de prédictions avec pattern page_XX
    prediction_files = glob.glob(os.path.join(predictions_dir, "page_*_*.json"))
    
    for pred_file in prediction_files:
        basename = os.path.basename(pred_file)
        # Extraire le préfixe page_XX
        parts = basename.split('_')
        if len(parts) >= 2 and parts[0] == 'page':
            page_prefix = f"{parts[0]}_{parts[1]}"  # page_02, page_03, etc.
            
            # Chercher le fichier GT correspondant
            gt_pattern = os.path.join(gt_dir, f"{page_prefix}_*_vt.json")
            gt_files = glob.glob(gt_pattern)
            
            if gt_files:
                page_mappings[page_prefix] = gt_files[0]
    
    return page_mappings

def main():
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    try:
        # Découvrir les mappings automatiquement
        page_mappings = discover_page_mappings(args.predictions_dir, args.gt_dir)
        
        if not page_mappings:
            print("Aucun mapping page/GT trouvé. Vérifiez les dossiers.", file=sys.stderr)
            sys.exit(1)
        
        # Filtrer par pages spécifiques si demandé
        if args.pages:
            page_mappings = {k: v for k, v in page_mappings.items() if k in args.pages}
        
        if not page_mappings:
            print("Aucune page correspondante trouvée.", file=sys.stderr)
            sys.exit(1)
        
        print(f"Mappings découverts: {len(page_mappings)}")
        for page, gt_file in page_mappings.items():
            print(f"  {page} -> {gt_file}")
        print("=" * 50)
        
        # Créer le dossier de sortie
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Traiter chaque mapping
        success_count = 0
        for page_prefix, gt_file in page_mappings.items():
            # Créer le pattern de prédictions pour cette page
            predictions_pattern = os.path.join(args.predictions_dir, f"{page_prefix}_*.json")
            
            # Vérifier qu'il y a des fichiers correspondants
            matching_files = glob.glob(predictions_pattern)
            if not matching_files:
                print(f"Aucun fichier trouvé pour le pattern: {predictions_pattern}")
                continue
            
            # Créer le dossier de sortie pour cette page
            output_dir = os.path.join(args.output_dir, page_prefix)
            
            # Exécuter la commande d'évaluation
            success = run_evaluation_command(gt_file, predictions_pattern, output_dir, args.distance)
            
            if success:
                print(f"✓ Évaluation terminée pour {page_prefix}")
                success_count += 1
            else:
                print(f"✗ Échec de l'évaluation pour {page_prefix}")
            print("-" * 50)
        
        print(f"Terminé: {success_count}/{len(page_mappings)} évaluations réussies")
        
    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()