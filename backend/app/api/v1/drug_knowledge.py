"""
毒品知識庫管理 API
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.responses import JSONResponse, FileResponse
import pandas as pd
import json
import logging
from datetime import datetime
import io

from app.schemas.upload import UploadRecordResponse
from app.services.knowledge_manager import KnowledgeManager
from app.models.upload import UploadType

logger = logging.getLogger(__name__)

router = APIRouter(tags=["drug-knowledge"])

# 服務實例
knowledge_manager = KnowledgeManager()


@router.post("/drug-knowledge/upload-excel", response_model=UploadRecordResponse)
async def upload_drug_knowledge_excel(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    uploaded_by: str = Form(...),
    batch_name: Optional[str] = Form(None)
):
    """
    上傳毒品知識庫 Excel 檔案
    
    Excel 格式要求：
    - 正式名稱 | 俗名（逗號分隔） | 管制等級 | 醫療用途 | 健康風險 | 相關法條 | 備註
    """
    try:
        # 驗證檔案類型
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(status_code=400, detail="請上傳 Excel 或 CSV 檔案")
        
        # 讀取檔案
        content = await file.read()
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
        
        # 驗證必要欄位
        required_columns = ['正式名稱', '管制等級']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"缺少必要欄位：{', '.join(missing_columns)}"
            )
        
        # 處理並儲存資料
        processed_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # 準備知識文件
                knowledge_doc = {
                    "title": f"毒品資訊：{row['正式名稱']}",
                    "content": _format_drug_content(row),
                    "source": "drug_database",
                    "category": "drug_information",
                    "metadata": {
                        "formal_name": row['正式名稱'],
                        "common_names": _parse_common_names(row.get('俗名', '')),
                        "control_level": row['管制等級'],
                        "medical_use": row.get('醫療用途', ''),
                        "health_risks": row.get('健康風險', ''),
                        "legal_info": row.get('相關法條', ''),
                        "uploaded_by": uploaded_by,
                        "batch_name": batch_name or f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    }
                }
                
                # 背景任務處理
                background_tasks.add_task(
                    knowledge_manager.add_knowledge_document,
                    knowledge_doc
                )
                
                processed_count += 1
                
            except Exception as e:
                errors.append(f"第 {index + 2} 行錯誤：{str(e)}")
        
        # 回傳結果
        return UploadRecordResponse(
            id="generated_id",
            filename=file.filename,
            upload_type=UploadType.AUTHORITY_MEDIA,
            status="processing",
            message=f"成功處理 {processed_count} 筆資料",
            errors=errors if errors else None
        )
        
    except Exception as e:
        logger.error(f"Error uploading drug knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/drug-knowledge/upload-json", response_model=UploadRecordResponse)
async def upload_drug_knowledge_json(
    background_tasks: BackgroundTasks,
    data: List[Dict[str, Any]]
):
    """
    上傳毒品知識庫 JSON 格式資料
    
    JSON 格式範例：
    [
        {
            "formal_name": "甲基安非他命",
            "common_names": ["冰毒", "冰塊", "煙仔", "豬肉"],
            "control_level": "第二級",
            "medical_use": "無合法醫療用途",
            "health_risks": "成癮性高、損害中樞神經...",
            "legal_info": "毒品危害防制條例第4條..."
        }
    ]
    """
    try:
        processed_count = 0
        
        for item in data:
            # 驗證必要欄位
            if not item.get('formal_name') or not item.get('control_level'):
                continue
            
            # 準備知識文件
            knowledge_doc = {
                "title": f"毒品資訊：{item['formal_name']}",
                "content": _format_drug_content_from_dict(item),
                "source": "drug_database",
                "category": "drug_information",
                "metadata": item
            }
            
            # 背景任務處理
            background_tasks.add_task(
                knowledge_manager.add_knowledge_document,
                knowledge_doc
            )
            
            processed_count += 1
        
        return UploadRecordResponse(
            id="generated_id",
            filename="json_upload",
            upload_type=UploadType.AUTHORITY_MEDIA,
            status="processing",
            message=f"成功處理 {processed_count} 筆資料"
        )
        
    except Exception as e:
        logger.error(f"Error uploading drug knowledge JSON: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drug-knowledge/template")
async def download_template():
    """下載毒品知識庫上傳模板"""
    
    # 建立範例資料
    template_data = {
        '正式名稱': ['甲基安非他命', '海洛因', '大麻'],
        '俗名（逗號分隔）': ['冰毒,冰塊,煙仔', '白粉,四號', '草,葉子,飛行員巧克力'],
        '管制等級': ['第二級', '第一級', '第二級'],
        '醫療用途': ['無', '無', '部分國家允許醫療使用'],
        '健康風險': [
            '成癮性高、損害中樞神經、心血管疾病',
            '極高成癮性、呼吸抑制、過量致死',
            '認知功能受損、呼吸系統問題'
        ],
        '相關法條': [
            '毒品危害防制條例第4條',
            '毒品危害防制條例第4條',
            '毒品危害防制條例第4條'
        ],
        '備註': ['', '', '']
    }
    
    # 建立 DataFrame
    df = pd.DataFrame(template_data)
    
    # 儲存為 Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='毒品知識庫')
        
        # 調整欄寬
        worksheet = writer.sheets['毒品知識庫']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    
    return FileResponse(
        io.BytesIO(output.read()),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename=f'毒品知識庫模板_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )


@router.get("/drug-knowledge/list")
async def list_drug_knowledge(
    skip: int = 0,
    limit: int = 100
):
    """列出已上傳的毒品知識"""
    try:
        # 從知識庫查詢毒品資訊
        results = await knowledge_manager.list_knowledge_documents(
            filters={"category": "drug_information"},
            skip=skip,
            limit=limit
        )
        
        return {
            "total": len(results),
            "items": results
        }
        
    except Exception as e:
        logger.error(f"Error listing drug knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/drug-knowledge/{drug_id}")
async def delete_drug_knowledge(drug_id: str):
    """刪除特定毒品知識"""
    try:
        success = await knowledge_manager.delete_knowledge_document(drug_id)
        
        if success:
            return {"message": "成功刪除"}
        else:
            raise HTTPException(status_code=404, detail="找不到該筆資料")
            
    except Exception as e:
        logger.error(f"Error deleting drug knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _format_drug_content(row: pd.Series) -> str:
    """格式化毒品資訊為文字內容"""
    content_parts = [
        f"毒品正式名稱：{row['正式名稱']}",
        f"管制藥品分級：{row['管制等級']}",
    ]
    
    if pd.notna(row.get('俗名')):
        content_parts.append(f"常見俗名：{row['俗名']}")
    
    if pd.notna(row.get('醫療用途')):
        content_parts.append(f"醫療用途：{row['醫療用途']}")
    
    if pd.notna(row.get('健康風險')):
        content_parts.append(f"健康風險：{row['健康風險']}")
    
    if pd.notna(row.get('相關法條')):
        content_parts.append(f"相關法條：{row['相關法條']}")
    
    if pd.notna(row.get('備註')):
        content_parts.append(f"其他說明：{row['備註']}")
    
    return '\n'.join(content_parts)


def _format_drug_content_from_dict(data: Dict) -> str:
    """從字典格式化毒品資訊"""
    content_parts = [
        f"毒品正式名稱：{data['formal_name']}",
        f"管制藥品分級：{data['control_level']}",
    ]
    
    if data.get('common_names'):
        names = data['common_names'] if isinstance(data['common_names'], list) else [data['common_names']]
        content_parts.append(f"常見俗名：{', '.join(names)}")
    
    if data.get('medical_use'):
        content_parts.append(f"醫療用途：{data['medical_use']}")
    
    if data.get('health_risks'):
        content_parts.append(f"健康風險：{data['health_risks']}")
    
    if data.get('legal_info'):
        content_parts.append(f"相關法條：{data['legal_info']}")
    
    return '\n'.join(content_parts)


def _parse_common_names(names_str: str) -> List[str]:
    """解析俗名字串"""
    if not names_str:
        return []
    
    # 支援多種分隔符號
    import re
    names = re.split('[,，、;；]', names_str)
    return [name.strip() for name in names if name.strip()]