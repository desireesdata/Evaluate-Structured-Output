#!/usr/bin/env python3
import os
import subprocess
import glob
import argparse
import sys
import csv
import re

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

def extract_stats_from_file(stats_file):
    """Extract statistics from a stats.txt file"""
    if not os.path.exists(stats_file):
        return None
    
    stats = {}
    with open(stats_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Extract metrics using regex
    precision_match = re.search(r'Precision: ([\d.]+)', content)
    recall_match = re.search(r'Recall: ([\d.]+)', content)
    f1_match = re.search(r'F1: ([\d.]+)', content)
    avg_quality_match = re.search(r'Average Matching Quality: ([\d.]+)', content)
    overall_quality_match = re.search(r'Overall Matching Quality: ([\d.]+)', content)
    imq_match = re.search(r'Integrated Matching Quality: ([\d.]+)', content)
    omq_imq_match = re.search(r'Overall Matching Quality \(IMQ-based\): ([\d.]+)', content)
    nb_truth_match = re.search(r'Nombre d\'entrées vérité terrain: (\d+)', content)
    nb_predicted_match = re.search(r'Nombre d\'entrées prédites: (\d+)', content)
    nb_matches_match = re.search(r'Nombre d\'appariements: (\d+)', content)
    
    # Extract predicted file name for source identification
    predicted_match = re.search(r'Predicted: ([^\n]+)', content)
    
    if precision_match:
        stats['precision'] = float(precision_match.group(1))
    if recall_match:
        stats['recall'] = float(recall_match.group(1))
    if f1_match:
        stats['f1'] = float(f1_match.group(1))
    if avg_quality_match:
        stats['avg_quality'] = float(avg_quality_match.group(1))
    if overall_quality_match:
        stats['overall_quality'] = float(overall_quality_match.group(1))
    if imq_match:
        stats['imq'] = float(imq_match.group(1))
    if omq_imq_match:
        stats['omq_imq'] = float(omq_imq_match.group(1))
    if nb_truth_match:
        stats['nb_truth'] = int(nb_truth_match.group(1))
    if nb_predicted_match:
        stats['nb_predicted'] = int(nb_predicted_match.group(1))
    if nb_matches_match:
        stats['nb_matches'] = int(nb_matches_match.group(1))
    if predicted_match:
        stats['predicted_file'] = predicted_match.group(1)
    
    return stats

def get_source_name(predicted_file):
    """Extract a human-readable source name from the predicted file path"""
    if not predicted_file:
        return "Unknown"
    
    filename = os.path.basename(predicted_file)
    
    # Keep original filename without extension for better traceability
    base_name = filename.replace('.json', '')
    return base_name

def consolidate_results(output_dir):
    """Consolidate all evaluation results into summary files"""
    all_stats = []
    all_csv_content = []
    all_txt_content = []
    
    # Find all stats files recursively
    stats_files = glob.glob(os.path.join(output_dir, "**", "*_stats.txt"), recursive=True)
    csv_files = glob.glob(os.path.join(output_dir, "**", "*_matches.csv"), recursive=True)
    
    # Process stats files
    for stats_file in stats_files:
        stats = extract_stats_from_file(stats_file)
        if stats:
            source_name = get_source_name(stats.get('predicted_file', ''))
            stats['source'] = source_name
            all_stats.append(stats)
            
            # Read the full txt content
            with open(stats_file, 'r', encoding='utf-8') as f:
                content = f.read()
                all_txt_content.append(f"=== {source_name} ===\n{content}\n")
    
    # Process CSV files
    for csv_file in csv_files:
        with open(csv_file, 'r', encoding='utf-8') as f:
            content = f.read()
            source_name = get_source_name(csv_file)
            all_csv_content.append(f"=== {source_name} ===\n{content}\n")
    
    # Write consolidated TXT file
    consolidated_txt_path = os.path.join(output_dir, "consolidated_results.txt")
    with open(consolidated_txt_path, 'w', encoding='utf-8') as f:
        f.write("CONSOLIDATED EVALUATION RESULTS\n")
        f.write("=" * 50 + "\n\n")
        f.write("\n".join(all_txt_content))
    
    # Write consolidated CSV file
    consolidated_csv_path = os.path.join(output_dir, "consolidated_matches.csv")
    with open(consolidated_csv_path, 'w', encoding='utf-8') as f:
        f.write("SOURCE\tTruth_Index\tPredicted_Index\tTruth_Nom\tPredicted_Nom\tTruth_Pages\tPredicted_Pages\tDistance\tQuality\n")
        for i, content in enumerate(all_csv_content):
            lines = content.strip().split('\n')
            source_name = lines[0].replace('=== ', '').replace(' ===', '')
            for line in lines[2:]:  # Skip header and source name
                if line.strip():
                    f.write(f"{source_name}\t{line}\n")
    
    # Write summary table CSV
    summary_csv_path = os.path.join(output_dir, "summary_table.csv")
    with open(summary_csv_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow([
            'Source', 'Precision', 'Recall', 'F1', 
            'Average Matching Quality', 'Overall Matching Quality',
            'Integrated Matching Quality', 'Overall Matching Quality (IMQ-based)',
            'Nombre d\'entrées vérité terrain', 'Nombre d\'entrées prédites', 
            'Nombre d\'appariements'
        ])
        
        for stats in all_stats:
            writer.writerow([
                stats.get('source', 'Unknown'),
                f"{stats.get('precision', 0):.4f}",
                f"{stats.get('recall', 0):.4f}",
                f"{stats.get('f1', 0):.4f}",
                f"{stats.get('avg_quality', 0):.4f}",
                f"{stats.get('overall_quality', 0):.4f}",
                f"{stats.get('imq', 0):.4f}",
                f"{stats.get('omq_imq', 0):.4f}",
                stats.get('nb_truth', 0),
                stats.get('nb_predicted', 0),
                stats.get('nb_matches', 0)
            ])
    
    print(f"\nFichiers consolidés générés:")
    print(f"  - {consolidated_txt_path}")
    print(f"  - {consolidated_csv_path}")
    print(f"  - {summary_csv_path}")
    
    return consolidated_txt_path, consolidated_csv_path, summary_csv_path


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
        
        # Generate consolidated files
        if success_count > 0:
            print("\nGénération des fichiers consolidés...")
            consolidate_results(args.output_dir)
        
    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()