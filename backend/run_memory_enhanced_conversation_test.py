"""基於長對話測試案例.md的記憶增強測試腳本"""

import asyncio
import json
import time
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple
from app.services.chat import ChatService
from app.schemas.chat import ChatRequest
from app.utils.quality_logger import get_quality_logger

# 確保使用UltimateWorkflow
os.environ["USE_ULTIMATE_WORKFLOW"] = "true"


class MemoryEnhancedTestRunner:
    """記憶增強長對話測試執行器"""
    
    def __init__(self):
        self.chat_service = ChatService()
        self.quality_logger = get_quality_logger()
        self.results = []
        
    def get_test_cases(self) -> Dict[str, List[Dict]]:
        """基於長對話測試案例.md的完整測試案例"""
        
        return {
            "個人資訊記憶": [
                {
                    "id": "personal_1_1",
                    "description": "基本資訊追蹤",
                    "conversation": [
                        {"user": "我叫阿明，今年35歲，住在高雄"},
                        {"user": "我有兩個小孩，一個8歲一個5歲"},
                        {"user": "我最近壓力很大，想找人聊聊"},
                        {"user": "你還記得我幾歲嗎？"}
                    ],
                    "expected": "您35歲，有兩個孩子（8歲和5歲），最近壓力較大"
                },
                {
                    "id": "personal_1_2",
                    "description": "複雜資訊串連",
                    "conversation": [
                        {"user": "我是小美，在工廠上班"},
                        {"user": "我每天早上6點就要起床"},
                        {"user": "下班後還要照顧生病的媽媽"},
                        {"user": "剛剛說的工作和家庭狀況，哪個讓我壓力比較大？"}
                    ],
                    "expected": "根據您的描述，照顧生病的媽媽和早起工作都是壓力源，需要同時兼顧工作與照護責任"
                }
            ],
            
            "情緒狀態追蹤": [
                {
                    "id": "emotion_2_1",
                    "description": "情緒變化記憶",
                    "conversation": [
                        {"user": "今天心情很差，被老闆罵了"},
                        {"user": "而且還被扣薪水"},
                        {"user": "不過下午同事請我喝咖啡，心情好一點了"},
                        {"user": "你覺得我現在心情如何？"}
                    ],
                    "expected": "經歷了被罵和扣薪的低潮後，因為同事的關心，您的心情有所好轉"
                },
                {
                    "id": "emotion_2_2",
                    "description": "複雜情緒理解",
                    "conversation": [
                        {"user": "我對戒毒這件事既期待又害怕"},
                        {"user": "期待是因為想重新開始"},
                        {"user": "但又怕失敗讓家人失望"},
                        {"user": "我的心情是什麼？"}
                    ],
                    "expected": "您對戒毒抱持希望但也有恐懼，期待新生活但擔心讓家人失望，這種複雜情緒很正常"
                }
            ],
            
            "時間序列事件": [
                {
                    "id": "time_3_1",
                    "description": "事件順序記憶",
                    "conversation": [
                        {"user": "上週一我去了醫院檢查"},
                        {"user": "週三參加了團體治療"},
                        {"user": "週五和家人吃飯"},
                        {"user": "這週發生了哪些事？"}
                    ],
                    "expected": "您這週一去醫院檢查、週三參加團體治療、週五和家人聚餐"
                },
                {
                    "id": "time_3_2",
                    "description": "時間關聯推理",
                    "conversation": [
                        {"user": "我已經戒毒3個月了"},
                        {"user": "下個月就是我女兒生日"},
                        {"user": "希望能保持到那時候"},
                        {"user": "到女兒生日我能戒毒多久？"}
                    ],
                    "expected": "到下個月您女兒生日時，您就戒毒4個月了"
                }
            ],
            
            "問題解決脈絡": [
                {
                    "id": "problem_4_1",
                    "description": "問題發展追蹤",
                    "conversation": [
                        {"user": "最近睡不好"},
                        {"user": "主要是一直做惡夢"},
                        {"user": "夢到以前吸毒的事"},
                        {"user": "我的睡眠問題根源是什麼？"}
                    ],
                    "expected": "您的睡眠問題主要是因為惡夢，而惡夢內容與過去吸毒經歷有關"
                },
                {
                    "id": "problem_4_2",
                    "description": "解決方案累積",
                    "conversation": [
                        {"user": "想找方法減壓"},
                        {"user": "我試過運動但膝蓋受傷了"},
                        {"user": "冥想我覺得太無聊"},
                        {"user": "有什麼適合我的減壓方法？"}
                    ],
                    "expected": "考慮您膝蓋受傷不適合運動、對冥想沒興趣，建議嘗試音樂、繪畫或其他靜態活動"
                }
            ],
            
            "人際關係網絡": [
                {
                    "id": "relation_5_1",
                    "description": "關係人物記憶",
                    "conversation": [
                        {"user": "我太太一直支持我"},
                        {"user": "但我哥哥不相信我能戒毒"},
                        {"user": "朋友阿強也在戒毒"},
                        {"user": "誰對我的戒毒最有幫助？"}
                    ],
                    "expected": "您太太的支持和朋友阿強的共同努力對您幫助最大，哥哥雖不相信但可以用行動證明"
                },
                {
                    "id": "relation_5_2",
                    "description": "關係動態變化",
                    "conversation": [
                        {"user": "老闆之前很信任我"},
                        {"user": "但發現我的過去後態度變了"},
                        {"user": "現在對我很冷淡"},
                        {"user": "老闆對我的態度怎麼變化？"}
                    ],
                    "expected": "老闆從原本的信任，在知道您的過去後轉為冷淡，需要時間重建關係"
                }
            ],
            
            "目標與進展": [
                {
                    "id": "goal_6_1",
                    "description": "目標設定追蹤",
                    "conversation": [
                        {"user": "我的目標是找到工作"},
                        {"user": "還想修復家庭關係"},
                        {"user": "最重要是保持清醒"},
                        {"user": "我設定了哪些目標？"}
                    ],
                    "expected": "您設定了三個目標：保持清醒（最重要）、找到工作、修復家庭關係"
                },
                {
                    "id": "goal_6_2",
                    "description": "進展評估記憶",
                    "conversation": [
                        {"user": "上個月體重增加了3公斤"},
                        {"user": "這個月又增加2公斤"},
                        {"user": "醫生說狀況不錯"},
                        {"user": "我的身體恢復如何？"}
                    ],
                    "expected": "您兩個月共增重5公斤，醫生認為恢復狀況良好"
                }
            ],
            
            "建議與反饋": [
                {
                    "id": "advice_7_1",
                    "description": "建議執行追蹤",
                    "conversation": [
                        {"user": "你上次建議我寫日記"},
                        {"user": "我試了一週覺得有用"},
                        {"user": "特別是睡前寫能放鬆"},
                        {"user": "你的什麼建議對我有用？"}
                    ],
                    "expected": "我建議您寫日記，您執行一週後發現有用，特別是睡前寫能幫助放鬆"
                },
                {
                    "id": "advice_7_2",
                    "description": "多重建議整合",
                    "conversation": [
                        {"user": "關於運動你說過什麼？"},
                        {"user": "飲食方面呢？"},
                        {"user": "作息你也提過"},
                        {"user": "整體來說你建議我注意什麼？"}
                    ],
                    "expected": "我建議您注意三方面：適度運動、均衡飲食、規律作息，形成健康生活型態"
                }
            ],
            
            "矛盾陳述識別": [
                {
                    "id": "conflict_8_1",
                    "description": "前後不一致檢測",
                    "conversation": [
                        {"user": "我昨天沒有碰毒品"},
                        {"user": "已經一個月沒碰了"},
                        {"user": "其實上週末有點失控"},
                        {"user": "我到底多久沒碰毒品？"}
                    ],
                    "expected": "您的說法有些矛盾，提到一個月沒碰但又說上週末失控，需要誠實面對現況"
                },
                {
                    "id": "conflict_8_2",
                    "description": "情緒矛盾理解",
                    "conversation": [
                        {"user": "我很開心終於戒毒了"},
                        {"user": "但又覺得很空虛"},
                        {"user": "不知道該開心還是難過"},
                        {"user": "我的真實感受是什麼？"}
                    ],
                    "expected": "您同時感到戒毒的成就感和生活的空虛感，這種矛盾情緒在康復過程中很正常"
                }
            ]
        }
    
    async def run_conversation(self, category: str, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """執行單一長對話測試案例，使用正確的UUID管理"""
        
        case_id = case_data["id"]
        description = case_data["description"]
        conversation = case_data["conversation"]
        expected_answer = case_data["expected"]
        
        # 使用正確的UUID管理方式
        user_id = f"memory_test_{category}_{case_id}"
        conversation_history = []
        response_times = []
        conversation_id = None  # 初始化為None，讓系統自動生成UUID
        
        try:
            # 執行對話的每一輪
            for i, turn in enumerate(conversation):
                if 'user' in turn:
                    request = ChatRequest(
                        user_id=user_id,
                        message=turn['user'],
                        conversation_id=conversation_id  # 第一次為None，後續使用系統生成的UUID
                    )
                    
                    start_time = time.time()
                    response = await self.chat_service.process_message(request)
                    response_time = time.time() - start_time
                    
                    # 第一次請求後保存系統生成的 conversation_id
                    if conversation_id is None:
                        conversation_id = response.conversation_id
                    
                    conversation_history.append({
                        "turn": i + 1,
                        "user": turn['user'],
                        "ai": response.reply,
                        "response_time": round(response_time, 2)
                    })
                    response_times.append(response_time)
                    
                    # 控制請求頻率，避免過快
                    await asyncio.sleep(0.5)
            
            # 評估最後一個回應
            last_response = conversation_history[-1]['ai'] if conversation_history else ""
            evaluation = self.evaluate_memory_quality(
                last_response=last_response,
                expected_answer=expected_answer,
                conversation_history=conversation_history,
                category=category
            )
            
            result = {
                "category": category,
                "case_id": case_id,
                "description": description,
                "conversation_id": str(conversation_id),  # 轉換UUID為字符串
                "conversation_history": conversation_history,
                "expected_answer": expected_answer,
                "actual_answer": last_response,
                "total_turns": len(conversation_history),
                "avg_response_time": round(sum(response_times) / len(response_times), 2) if response_times else 0,
                "evaluation": evaluation,
                "success": evaluation["score"] >= 70,
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            return {
                "category": category,
                "case_id": case_id,
                "description": description,
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
    
    def evaluate_memory_quality(self, last_response: str, expected_answer: str,
                               conversation_history: List[Dict], category: str) -> Dict[str, Any]:
        """評估記憶品質的詳細評分"""
        
        evaluation = {
            "score": 0,
            "details": {},
            "memory_aspects": {}
        }
        
        # 基本相似性評分 (40分)
        similarity_score = self.calculate_semantic_similarity(last_response, expected_answer)
        evaluation["details"]["semantic_similarity"] = similarity_score
        
        # 記憶完整性評分 (30分)
        memory_completeness = self.evaluate_memory_completeness(
            last_response, conversation_history, category
        )
        evaluation["memory_aspects"]["completeness"] = memory_completeness
        
        # 記憶準確性評分 (20分) 
        memory_accuracy = self.evaluate_memory_accuracy(
            last_response, conversation_history
        )
        evaluation["memory_aspects"]["accuracy"] = memory_accuracy
        
        # 上下文連貫性評分 (10分)
        context_coherence = self.evaluate_context_coherence(
            last_response, conversation_history
        )
        evaluation["memory_aspects"]["coherence"] = context_coherence
        
        # 計算總分
        total_score = (
            similarity_score * 0.4 +
            memory_completeness * 0.3 +
            memory_accuracy * 0.2 +
            context_coherence * 0.1
        )
        
        evaluation["score"] = round(total_score, 1)
        
        # 評級
        if total_score >= 90:
            evaluation["grade"] = "優秀"
        elif total_score >= 70:
            evaluation["grade"] = "良好"
        else:
            evaluation["grade"] = "待改進"
        
        return evaluation
    
    def calculate_semantic_similarity(self, actual: str, expected: str) -> float:
        """計算語義相似性（簡化版本）"""
        
        # 提取關鍵詞
        actual_words = set(actual.replace('，', ' ').replace('。', ' ').split())
        expected_words = set(expected.replace('，', ' ').replace('。', ' ').split())
        
        if not expected_words:
            return 0.0
        
        # 計算重疊率
        common_words = actual_words & expected_words
        similarity = len(common_words) / len(expected_words)
        
        return min(similarity * 100, 100)
    
    def evaluate_memory_completeness(self, response: str, history: List[Dict], category: str) -> float:
        """評估記憶完整性"""
        
        # 提取對話中的關鍵資訊
        key_info = []
        for turn in history[:-1]:  # 排除最後一輪問題
            user_msg = turn.get("user", "")
            
            # 根據類別提取不同類型的關鍵資訊
            if category == "個人資訊記憶":
                key_info.extend(self.extract_personal_info(user_msg))
            elif category == "情緒狀態追蹤":
                key_info.extend(self.extract_emotional_info(user_msg))
            elif category == "時間序列事件":
                key_info.extend(self.extract_temporal_info(user_msg))
            # 其他類別可以繼續擴展
        
        if not key_info:
            return 100.0
        
        # 檢查回應中包含多少關鍵資訊
        mentioned_info = sum(1 for info in key_info if info in response)
        completeness = mentioned_info / len(key_info) * 100
        
        return min(completeness, 100)
    
    def extract_personal_info(self, text: str) -> List[str]:
        """提取個人資訊"""
        info = []
        
        # 姓名
        if "叫" in text:
            info.append(text.split("叫")[1].split("，")[0].split(" ")[0])
        
        # 年齡
        import re
        age_match = re.search(r'(\d+)歲', text)
        if age_match:
            info.append(age_match.group(0))
        
        # 地點
        if "住在" in text:
            location = text.split("住在")[1].split("，")[0].split(" ")[0]
            info.append(location)
        
        # 工作
        if "上班" in text or "工作" in text:
            info.append("工作")
        
        return info
    
    def extract_emotional_info(self, text: str) -> List[str]:
        """提取情緒資訊"""
        emotions = []
        
        emotion_keywords = ["開心", "難過", "害怕", "期待", "擔心", "焦慮", "憤怒", "失望"]
        for emotion in emotion_keywords:
            if emotion in text:
                emotions.append(emotion)
        
        return emotions
    
    def extract_temporal_info(self, text: str) -> List[str]:
        """提取時間資訊"""
        temporal = []
        
        time_keywords = ["週一", "週二", "週三", "週四", "週五", "週六", "週日", 
                        "上週", "這週", "下週", "個月", "年"]
        for keyword in time_keywords:
            if keyword in text:
                temporal.append(keyword)
        
        return temporal
    
    def evaluate_memory_accuracy(self, response: str, history: List[Dict]) -> float:
        """評估記憶準確性"""
        
        # 檢查是否有明顯的記憶錯誤
        accuracy_score = 100.0
        
        # 檢查是否有矛盾資訊
        contradictions = self.detect_contradictions(response, history)
        accuracy_score -= len(contradictions) * 20
        
        return max(accuracy_score, 0)
    
    def detect_contradictions(self, response: str, history: List[Dict]) -> List[str]:
        """檢測矛盾"""
        contradictions = []
        
        # 簡化的矛盾檢測 - 可以進一步完善
        # 這裡可以實作更複雜的邏輯
        
        return contradictions
    
    def evaluate_context_coherence(self, response: str, history: List[Dict]) -> float:
        """評估上下文連貫性"""
        
        if len(history) <= 1:
            return 100.0
        
        # 檢查回應是否與最近的對話相關
        last_user_message = history[-1].get("user", "")
        
        # 簡化的連貫性檢查
        coherence_score = 80.0  # 基礎分數
        
        # 如果回應長度太短，可能缺乏上下文
        if len(response) < 20:
            coherence_score -= 20
        
        return coherence_score
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """執行所有測試案例"""
        
        print("🚀 開始記憶增強長對話測試")
        print("=" * 60)
        
        test_cases = self.get_test_cases()
        all_results = []
        category_stats = {}
        
        total_cases = sum(len(cases) for cases in test_cases.values())
        current_case = 0
        
        for category, cases in test_cases.items():
            print(f"\n📊 測試類別：{category}")
            print("-" * 40)
            
            category_results = []
            
            for case in cases:
                current_case += 1
                print(f"  {current_case}/{total_cases} 執行：{case['description']}")
                
                result = await self.run_conversation(category, case)
                category_results.append(result)
                all_results.append(result)
                
                # 顯示結果
                if result.get("success", False):
                    score = result["evaluation"]["score"]
                    grade = result["evaluation"]["grade"]
                    print(f"    ✅ 成功 - 分數：{score}/100 ({grade})")
                else:
                    print(f"    ❌ 失敗 - {result.get('error', '未知錯誤')}")
            
            # 計算類別統計
            successful_cases = [r for r in category_results if r.get("success", False)]
            if successful_cases:
                avg_score = sum(r["evaluation"]["score"] for r in successful_cases) / len(successful_cases)
                success_rate = len(successful_cases) / len(category_results) * 100
                
                category_stats[category] = {
                    "total_cases": len(category_results),
                    "successful_cases": len(successful_cases),
                    "success_rate": success_rate,
                    "average_score": round(avg_score, 1)
                }
                
                print(f"  📈 {category}統計：成功率 {success_rate:.1f}%，平均分數 {avg_score:.1f}")
            else:
                category_stats[category] = {
                    "total_cases": len(category_results),
                    "successful_cases": 0,
                    "success_rate": 0,
                    "average_score": 0
                }
                print(f"  📈 {category}統計：全部失敗")
        
        # 計算總體統計
        successful_results = [r for r in all_results if r.get("success", False)]
        overall_success_rate = len(successful_results) / len(all_results) * 100 if all_results else 0
        overall_avg_score = sum(r["evaluation"]["score"] for r in successful_results) / len(successful_results) if successful_results else 0
        
        # 生成報告
        report = {
            "test_info": {
                "timestamp": datetime.now().isoformat(),
                "total_test_cases": len(all_results),
                "successful_cases": len(successful_results),
                "overall_success_rate": round(overall_success_rate, 1),
                "overall_average_score": round(overall_avg_score, 1)
            },
            "category_statistics": category_stats,
            "detailed_results": all_results
        }
        
        # 保存報告
        report_filename = f"memory_enhanced_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 顯示總結
        print("\n" + "=" * 60)
        print("🏆 測試完成摘要")
        print("=" * 60)
        print(f"總測試案例：{len(all_results)}")
        print(f"成功案例：{len(successful_results)}")
        print(f"整體成功率：{overall_success_rate:.1f}%")
        print(f"整體平均分數：{overall_avg_score:.1f}/100")
        print(f"報告已保存：{report_filename}")
        
        return report


async def main():
    """主執行函數"""
    runner = MemoryEnhancedTestRunner()
    await runner.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())