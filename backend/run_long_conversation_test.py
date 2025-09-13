"""執行長對話測試案例的自動化腳本"""

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


class LongConversationTestRunner:
    """長對話測試執行器"""
    
    def __init__(self):
        self.chat_service = ChatService()
        self.quality_logger = get_quality_logger()
        self.results = []
        
    async def run_conversation(self, category: str, case_id: str, 
                             conversation: List[Dict[str, str]], 
                             expected_answer: str, description: str = "") -> Dict[str, Any]:
        """執行單一長對話測試"""
        
        user_id = f"long_test_{category}_{case_id}"
        conversation_history = []
        response_times = []
        conversation_id = None  # 初始化 conversation_id
        
        try:
            # 執行對話的每一輪
            for i, turn in enumerate(conversation):
                if 'user' in turn:
                    request = ChatRequest(
                        user_id=user_id,
                        message=turn['user'],
                        conversation_id=conversation_id  # 傳遞 conversation_id
                    )
                    
                    start_time = time.time()
                    response = await self.chat_service.process_message(request)
                    response_time = time.time() - start_time
                    
                    # 第一次請求後保存 conversation_id
                    if conversation_id is None:
                        conversation_id = response.conversation_id
                    
                    conversation_history.append({
                        "turn": i + 1,
                        "user": turn['user'],
                        "ai": response.reply,
                        "response_time": round(response_time, 2)
                    })
                    response_times.append(response_time)
                    
                    # 控制請求頻率
                    await asyncio.sleep(0.5)
            
            # 評估最後一個回應
            last_response = conversation_history[-1]['ai'] if conversation_history else ""
            evaluation = self.evaluate_response(
                last_response=last_response,
                expected_answer=expected_answer,
                conversation_history=conversation_history,
                response_times=response_times
            )
            
            result = {
                "category": category,
                "case_id": case_id,
                "description": description,
                "conversation_history": conversation_history,
                "expected_answer": expected_answer,
                "actual_answer": last_response,
                "total_turns": len(conversation_history),
                "avg_response_time": round(sum(response_times) / len(response_times), 2) if response_times else 0,
                "evaluation": evaluation,
                "success": evaluation["score"] >= 70
            }
            
            return result
            
        except Exception as e:
            return {
                "category": category,
                "case_id": case_id,
                "description": description,
                "error": str(e),
                "success": False
            }
    
    def evaluate_response(self, last_response: str, expected_answer: str,
                         conversation_history: List[Dict], 
                         response_times: List[float]) -> Dict[str, Any]:
        """評估長對話回應品質"""
        
        score = 100
        issues = []
        
        # 記憶準確度評估 (40分)
        memory_score = 40
        key_info_retained = []
        key_info_missing = []
        
        # 根據預期答案檢查關鍵資訊
        if "35歲" in expected_answer and "35" in last_response:
            key_info_retained.append("年齡")
        elif "35歲" in expected_answer and "35" not in last_response:
            key_info_missing.append("年齡")
            memory_score -= 10
            
        if "兩個" in expected_answer and ("兩個" in last_response or "2個" in last_response):
            key_info_retained.append("孩子數量")
        elif "兩個" in expected_answer and "兩個" not in last_response and "2個" not in last_response:
            key_info_missing.append("孩子數量")
            memory_score -= 10
            
        if "8歲" in expected_answer and "8" in last_response:
            key_info_retained.append("孩子年齡")
        elif "8歲" in expected_answer and "8" not in last_response:
            key_info_missing.append("孩子年齡細節")
            memory_score -= 5
            
        # 上下文理解評估 (30分)
        context_score = 30
        if len(conversation_history) > 2:
            # 檢查是否有整合多輪對話的跡象
            if not any(word in last_response for word in ["根據", "您提到", "之前說", "剛才"]):
                context_score -= 10
                issues.append("缺乏上下文引用")
        
        # 回應相關性評估 (20分)
        relevance_score = 20
        # 簡單檢查回應是否針對問題
        if "？" in conversation_history[-1]['user'] and len(last_response) < 10:
            relevance_score -= 10
            issues.append("回應過於簡短")
            
        # 性能評估 (10分)
        performance_score = 10
        avg_time = sum(response_times) / len(response_times) if response_times else 0
        if avg_time > 2.0:
            performance_score = 5
            issues.append("平均回應時間過長")
        elif avg_time > 3.0:
            performance_score = 0
            issues.append("回應速度嚴重過慢")
        
        total_score = memory_score + context_score + relevance_score + performance_score
        
        return {
            "score": max(0, min(100, total_score)),
            "memory_score": memory_score,
            "context_score": context_score,
            "relevance_score": relevance_score,
            "performance_score": performance_score,
            "key_info_retained": key_info_retained,
            "key_info_missing": key_info_missing,
            "issues": issues
        }


def get_long_conversation_test_cases() -> Dict[str, List[Dict]]:
    """取得長對話測試案例"""
    
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
        ],
        
        "觸發因素分析": [
            {
                "id": "trigger_9_1",
                "description": "壓力源識別",
                "conversation": [
                    {"user": "每次和前朋友見面就想復吸"},
                    {"user": "經過以前常去的地方也會"},
                    {"user": "壓力大的時候特別想"},
                    {"user": "什麼情況會讓我想復吸？"}
                ],
                "expected": "三個主要觸發因素：見到過去朋友、經過熟悉地點、承受壓力時"
            },
            {
                "id": "trigger_9_2",
                "description": "模式識別測試",
                "conversation": [
                    {"user": "週五晚上特別難熬"},
                    {"user": "以前都是週五聚會"},
                    {"user": "現在週五都很焦慮"},
                    {"user": "我的問題模式是什麼？"}
                ],
                "expected": "週五晚上因為過去聚會習慣，現在會特別焦慮，需要建立新的週五活動"
            }
        ],
        
        "長期變化追蹤": [
            {
                "id": "change_10_1",
                "description": "階段性變化記錄",
                "conversation": [
                    {"user": "剛開始戒毒時手一直抖"},
                    {"user": "第二週開始好轉"},
                    {"user": "現在第三週幾乎沒症狀了"},
                    {"user": "我的戒斷症狀如何變化？"}
                ],
                "expected": "從第一週手抖嚴重，第二週開始好轉，到第三週幾乎沒症狀，呈現穩定改善"
            },
            {
                "id": "change_10_2",
                "description": "心態演變追蹤",
                "conversation": [
                    {"user": "一開始我覺得不可能成功"},
                    {"user": "但團體治療讓我看到希望"},
                    {"user": "現在我相信自己可以"},
                    {"user": "我的心態怎麼改變的？"}
                ],
                "expected": "您從最初的沒信心，透過團體治療獲得希望，到現在建立自信，心態正向轉變"
            }
        ]
    }


async def main():
    """執行長對話測試"""
    
    print("\n" + "="*80)
    print("雄i聊系統 - 長對話測試案例執行")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    runner = LongConversationTestRunner()
    all_cases = get_long_conversation_test_cases()
    
    # 執行測試
    category_stats = []
    total_cases = 0
    
    for category_name, cases in all_cases.items():
        print(f"\n{'='*60}")
        print(f"測試類別: {category_name} ({len(cases)}個案例)")
        print(f"{'='*60}")
        
        category_results = []
        
        for i, case in enumerate(cases, 1):
            print(f"\n測試 {i}/{len(cases)}: {case['description']}")
            print(f"對話輪數: {len(case['conversation'])}")
            
            result = await runner.run_conversation(
                category=category_name,
                case_id=case['id'],
                conversation=case['conversation'],
                expected_answer=case['expected'],
                description=case['description']
            )
            
            if result.get('error'):
                print(f"❌ 錯誤: {result['error']}")
            else:
                print(f"最終回應: {result['actual_answer'][:100]}...")
                print(f"平均耗時: {result['avg_response_time']}秒")
                print(f"評分: {result['evaluation']['score']}/100")
                
                if result['evaluation']['key_info_retained']:
                    print(f"✅ 記住: {', '.join(result['evaluation']['key_info_retained'])}")
                if result['evaluation']['key_info_missing']:
                    print(f"❌ 遺忘: {', '.join(result['evaluation']['key_info_missing'])}")
                
                if result['success']:
                    print("✅ 通過")
                else:
                    print("⚠️ 需改進")
            
            category_results.append(result)
            runner.results.append(result)
            total_cases += 1
            
            # 控制請求頻率
            await asyncio.sleep(1)
        
        # 類別統計
        successful = [r for r in category_results if r.get('success', False)]
        if category_results:
            avg_score = sum(r['evaluation']['score'] for r in category_results if 'evaluation' in r) / len(category_results)
        else:
            avg_score = 0
            
        category_stats.append({
            "category": category_name,
            "total": len(cases),
            "passed": len(successful),
            "pass_rate": len(successful) / len(cases) * 100 if cases else 0,
            "average_score": avg_score
        })
    
    # 生成總報告
    print("\n" + "="*80)
    print("長對話測試總報告")
    print("="*80)
    
    total_passed = sum(stat['passed'] for stat in category_stats)
    overall_pass_rate = total_passed / total_cases * 100 if total_cases else 0
    overall_avg_score = sum(stat['average_score'] * stat['total'] for stat in category_stats) / total_cases if total_cases else 0
    
    print(f"\n📊 整體表現:")
    print(f"   總測試數: {total_cases}")
    print(f"   通過數: {total_passed}")
    print(f"   整體通過率: {overall_pass_rate:.1f}%")
    print(f"   整體平均分: {overall_avg_score:.1f}/100")
    
    print(f"\n📈 各類別表現:")
    for stat in category_stats:
        status = "🟢" if stat['pass_rate'] >= 80 else "🟡" if stat['pass_rate'] >= 60 else "🔴"
        print(f"   {status} {stat['category']}: {stat['pass_rate']:.1f}% (平均{stat['average_score']:.1f}分)")
    
    # 記憶能力分析
    memory_scores = []
    context_scores = []
    for result in runner.results:
        if 'evaluation' in result:
            memory_scores.append(result['evaluation']['memory_score'])
            context_scores.append(result['evaluation']['context_score'])
    
    if memory_scores:
        print(f"\n🧠 記憶能力分析:")
        print(f"   平均記憶分數: {sum(memory_scores)/len(memory_scores):.1f}/40")
        print(f"   平均上下文理解: {sum(context_scores)/len(context_scores):.1f}/30")
    
    # 性能統計
    all_response_times = []
    for result in runner.results:
        if 'avg_response_time' in result:
            all_response_times.append(result['avg_response_time'])
    
    if all_response_times:
        print(f"\n⏱️  性能統計:")
        print(f"   整體平均回應時間: {sum(all_response_times)/len(all_response_times):.2f}秒")
        print(f"   最快平均回應: {min(all_response_times):.2f}秒")
        print(f"   最慢平均回應: {max(all_response_times):.2f}秒")
    
    # 儲存詳細報告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"long_conversation_test_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_cases,
                "passed": total_passed,
                "pass_rate": overall_pass_rate,
                "average_score": overall_avg_score,
                "avg_memory_score": sum(memory_scores)/len(memory_scores) if memory_scores else 0,
                "avg_context_score": sum(context_scores)/len(context_scores) if context_scores else 0
            },
            "category_stats": category_stats,
            "detailed_results": runner.results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 詳細報告已儲存: {report_file}")
    
    # 匯出品質評估資料
    quality_logger = get_quality_logger()
    export_file = quality_logger.export_for_evaluation()
    print(f"📊 品質評估資料: {export_file}")
    
    print("\n" + "="*80)
    print("🎉 長對話測試執行完成！")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())