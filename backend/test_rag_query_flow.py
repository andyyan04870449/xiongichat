"""
測試RAG查詢流程，使用完整工作流追蹤分析過程
"""

import asyncio
import logging
import time
import re
from uuid import uuid4
from app.langgraph.ultimate_workflow import UltimateWorkflow

# 設定較低的日誌級別以顯示詳細資訊
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_rag_query_flow():
    """使用完整工作流測試RAG查詢流程"""
    
    # 測試案例
    test_queries = [
        "凱旋醫院的電話是多少",
        "我想知道凱旋醫院",
        "高雄市立凱旋醫院聯絡方式"
    ]
    
    # 初始化工作流
    workflow = UltimateWorkflow()
    user_id = "rag_test_user"
    conversation_id = str(uuid4())
    
    for i, user_message in enumerate(test_queries, 1):
        print(f"\n🧪 測試 {i}: {user_message}")
        print("="*80)
        
        # 準備輸入
        test_input = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "input_text": user_message
        }
        
        print(f"📝 用戶輸入: \"{user_message}\"")
        
        # 執行工作流
        start_time = time.time()
        try:
            result = await workflow.ainvoke(test_input)
            processing_time = time.time() - start_time
            
            # 提取分析結果
            intent_analysis = result.get('intent_analysis', {})
            rag_content = result.get('rag_content', {})
            ai_response = result.get('reply', '')
            
            print(f"\n🤖 AI回應: \"{ai_response}\"")
            print(f"⏱️ 處理時間: {processing_time:.2f}秒")
            
            # 顯示意圖分析結果
            print(f"\n🔍 意圖分析結果:")
            print(f"   情緒狀態: {intent_analysis.get('emotional_state', 'unknown')}")
            print(f"   風險等級: {intent_analysis.get('risk_level', 'unknown')}")
            print(f"   關懷階段: 第{intent_analysis.get('care_stage_needed', 'unknown')}層")
            print(f"   需要RAG: {intent_analysis.get('need_rag', False)}")
            print(f"   意圖類型: {intent_analysis.get('intent_type', 'unknown')}")
            
            # 顯示RAG檢索結果
            if intent_analysis.get('need_rag', False) and rag_content:
                print(f"\n📚 RAG檢索結果:")
                
                # 檢索統計
                if 'metadata' in rag_content:
                    metadata = rag_content['metadata']
                    print(f"   查詢字串: \"{metadata.get('query', 'N/A')}\"")
                    print(f"   檢索到: {metadata.get('total_results', 0)} 筆結果")
                    print(f"   最高相似度: {metadata.get('max_similarity', 0):.3f}")
                
                # 內容摘要
                content = rag_content.get('content', '')
                if content:
                    print(f"   內容長度: {len(content)} 字")
                    print(f"   內容預覽: {content[:150]}...")
                    
                    # 檢查是否包含聯絡資訊
                    phones = re.findall(r'(?:\(?\d{2,3}\)?[\s-]?\d{3,4}[\s-]?\d{4}|0\d{9,10}|0800[\s-]?\d{6})', content)
                    addresses = re.findall(r'地址[：:]\s*([^\\n]+)', content)
                    
                    if phones:
                        print(f"   📞 包含電話: {phones}")
                    if addresses:
                        print(f"   📍 包含地址: {addresses}")
                        
                    if phones or addresses:
                        print(f"   ✅ 成功檢索到聯絡資訊")
                    else:
                        print(f"   ⚠️ 未檢索到明確聯絡資訊")
                else:
                    print(f"   ❌ 無RAG內容")
            else:
                print(f"\n📚 RAG檢索: 未觸發RAG檢索")
            
            # 顯示關鍵分析指標
            print(f"\n📊 分析總結:")
            need_rag = intent_analysis.get('need_rag', False)
            has_rag_content = bool(rag_content.get('content'))
            has_contact_info = bool(re.search(r'(?:\(?\d{2,3}\)?[\s-]?\d{3,4}[\s-]?\d{4}|地址)', ai_response))
            
            print(f"   RAG觸發: {'✅' if need_rag else '❌'}")
            print(f"   RAG內容: {'✅' if has_rag_content else '❌'}")
            print(f"   包含聯絡資訊: {'✅' if has_contact_info else '❌'}")
            
            # 評估是否符合預期
            if "電話" in user_message or "聯絡" in user_message:
                expected_rag = True
                expected_contact = True
            else:
                expected_rag = True  # 凱旋醫院相關查詢都應該觸發RAG
                expected_contact = False  # 不一定需要包含聯絡資訊
                
            rag_correct = (need_rag == expected_rag)
            contact_appropriate = (has_contact_info == expected_contact) or has_contact_info  # 有聯絡資訊總是好的
            
            print(f"   符合預期: {'✅' if (rag_correct and contact_appropriate) else '❌'}")
            
        except Exception as e:
            print(f"❌ 執行失敗: {str(e)}")
        
        print("\n" + "="*80)
        
        # 短暫休息
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(test_rag_query_flow())