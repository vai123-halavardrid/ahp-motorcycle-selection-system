from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import pandas as pd
import os
from .database import (
    insert_alternative, insert_criteria_comparison, 
    insert_alternative_comparison, insert_final_result,
    get_alternatives, get_criteria_comparison, 
    get_alternative_comparisons, get_final_result
)
from .ahp import AHPCalculator
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import io

main_bp = Blueprint('main', __name__)

# Constants
CRITERIA = [
    'Ngân sách',
    'Kiểu dáng',
    'Hiệu suất & Công suất',
    'Tiết kiệm nhiên liệu',
    'Công nghệ & Tính năng',
    'Kích thước & Trọng lượng'
]

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@main_bp.route('/alternatives', methods=['GET', 'POST'])
def alternatives():
    """Handle alternative selection"""
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                try:
                    df = pd.read_excel(file)
                    required_columns = ['Tên xe máy'] + CRITERIA
                    if not all(col in df.columns for col in required_columns):
                        flash('File Excel không đúng định dạng. Vui lòng kiểm tra lại.', 'error')
                        return redirect(request.url)
                    
                    # Save alternatives to database
                    for _, row in df.iterrows():
                        alternative_data = {
                            'name': row['Tên xe máy'],
                            'criteria_values': {
                                criterion: row[criterion]
                                for criterion in CRITERIA
                            }
                        }
                        insert_alternative(alternative_data)
                    
                    flash('Import thành công!', 'success')
                except Exception as e:
                    flash(f'Lỗi khi xử lý file: {str(e)}', 'error')
                    return redirect(request.url)
        else:
            # Handle manual alternative input
            name = request.form.get('name')
            if name:
                try:
                    alternative_data = {
                        'name': name,
                        'criteria_values': {}  # Empty for manual input
                    }
                    insert_alternative(alternative_data)
                    flash('Thêm phương án thành công!', 'success')
                except Exception as e:
                    flash(f'Lỗi khi thêm phương án: {str(e)}', 'error')
                    return redirect(request.url)

    # Get all alternatives for display
    alternatives = get_alternatives()
    return render_template('alternatives.html', alternatives=alternatives)

@main_bp.route('/criteria-comparison', methods=['GET', 'POST'])
def criteria_comparison():
    """Handle criteria comparison matrix"""
    if request.method == 'POST':
        try:
            # Get matrix values from form
            matrix_values = []
            for i in range(len(CRITERIA)):
                row = []
                for j in range(i + 1, len(CRITERIA)):
                    value = request.form.get(f'comparison_{i}_{j}')
                    if value:
                        row.append(value)
                matrix_values.append(row)

            # Process the comparison matrix
            result = AHPCalculator.process_comparison_matrix(matrix_values, CRITERIA)
            
            if not result['is_consistent']:
                flash('Ma trận không nhất quán (CR > 0.1). Vui lòng nhập lại.', 'error')
                return redirect(request.url)

            # Save to database
            comparison_data = {
                'matrix': result['matrix'].tolist(),
                'weights': result['weights'].tolist(),
                'lambda_max': float(result['lambda_max']),
                'ci': float(result['ci']),
                'cr': float(result['cr'])
            }
            insert_criteria_comparison(comparison_data)
            
            flash('So sánh tiêu chí thành công!', 'success')
            return redirect(url_for('main.alternative_comparison', criterion_id=0))
            
        except Exception as e:
            flash(f'Lỗi: {str(e)}', 'error')
            return redirect(request.url)

    return render_template('criteria_comparison.html', criteria=CRITERIA)

@main_bp.route('/alternative-comparison/<int:criterion_id>', methods=['GET', 'POST'])
def alternative_comparison(criterion_id):
    """Handle alternative comparison for each criterion"""
    if criterion_id >= len(CRITERIA):
        return redirect(url_for('main.final_result'))

    alternatives = get_alternatives()
    if len(alternatives) < 3:
        flash('Cần ít nhất 3 phương án để tiếp tục.', 'error')
        return redirect(url_for('main.alternatives'))

    if request.method == 'POST':
        try:
            # Get matrix values from form
            matrix_values = []
            n = len(alternatives)
            for i in range(n):
                row = []
                for j in range(i + 1, n):
                    value = request.form.get(f'comparison_{i}_{j}')
                    if value:
                        row.append(value)
                matrix_values.append(row)

            # Process the comparison matrix
            result = AHPCalculator.process_comparison_matrix(
                matrix_values,
                [alt['name'] for alt in alternatives]
            )
            
            if not result['is_consistent']:
                flash('Ma trận không nhất quán (CR > 0.1). Vui lòng nhập lại.', 'error')
                return redirect(request.url)

            # Save to database
            comparison_data = {
                'criterion_id': criterion_id,
                'criterion_name': CRITERIA[criterion_id],
                'alternatives': [alt['name'] for alt in alternatives],
                'matrix': result['matrix'].tolist(),
                'weights': result['weights'].tolist(),
                'lambda_max': float(result['lambda_max']),
                'ci': float(result['ci']),
                'cr': float(result['cr'])
            }
            insert_alternative_comparison(comparison_data)
            
            flash('So sánh phương án thành công!', 'success')
            return redirect(url_for('main.alternative_comparison', criterion_id=criterion_id + 1))
            
        except Exception as e:
            flash(f'Lỗi: {str(e)}', 'error')
            return redirect(request.url)

    return render_template(
        'alternative_comparison.html',
        criterion=CRITERIA[criterion_id],
        alternatives=alternatives,
        criterion_id=criterion_id
    )

@main_bp.route('/final-result')
def final_result():
    """Calculate and display final results"""
    try:
        # Get all necessary data
        criteria_comparison = get_criteria_comparison()
        alternative_comparisons = get_alternative_comparisons()
        alternatives = get_alternatives()

        if not all([criteria_comparison, alternative_comparisons, alternatives]):
            flash('Thiếu dữ liệu để tính toán kết quả cuối cùng.', 'error')
            return redirect(url_for('main.alternatives'))

        # Calculate final scores
        criteria_weights = np.array(criteria_comparison['weights'])
        alternative_weights = {
            comp['criterion_name']: np.array(comp['weights'])
            for comp in alternative_comparisons
        }

        final_scores = AHPCalculator.calculate_final_scores(
            criteria_weights,
            alternative_weights
        )

        # Prepare results
        results = []
        for i, score in final_scores.items():
            results.append({
                'name': alternatives[i]['name'],
                'score': score,
                'percentage': score * 100
            })

        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Add rankings
        for i, result in enumerate(results, 1):
            result['rank'] = i

        # Generate conclusion
        conclusion = f"Dựa trên phân tích AHP, {results[0]['name']} là lựa chọn tốt nhất với điểm số {results[0]['score']:.4f} ({results[0]['percentage']:.2f}%)."

        # Save results
        result_data = {
            'results': results,
            'conclusion': conclusion
        }
        insert_final_result(result_data)

        return render_template('final_result.html', results=results, conclusion=conclusion)

    except Exception as e:
        flash(f'Lỗi khi tính toán kết quả: {str(e)}', 'error')
        return redirect(url_for('main.alternatives'))

@main_bp.route('/export/<format>')
def export_result(format):
    """Export results to Excel or PDF"""
    try:
        final_result = get_final_result()
        if not final_result:
            flash('Không có dữ liệu để xuất.', 'error')
            return redirect(url_for('main.final_result'))

        if format == 'excel':
            # Create Excel file
            output = io.BytesIO()
            df = pd.DataFrame(final_result['results'])
            df.to_excel(output, index=False)
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'ahp_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            )

        elif format == 'pdf':
            # Create PDF file
            output = io.BytesIO()
            
            # Create pie chart
            plt.figure(figsize=(8, 6))
            plt.pie(
                [r['percentage'] for r in final_result['results']],
                labels=[r['name'] for r in final_result['results']],
                autopct='%1.1f%%'
            )
            plt.title('Phân bố kết quả AHP')
            
            # Save plot to PDF
            plt.savefig(output, format='pdf')
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'ahp_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            )

        else:
            flash('Định dạng không hợp lệ.', 'error')
            return redirect(url_for('main.final_result'))

    except Exception as e:
        flash(f'Lỗi khi xuất kết quả: {str(e)}', 'error')
        return redirect(url_for('main.final_result'))
