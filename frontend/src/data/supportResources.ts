// 扶助資源的詳細資料
import { CommandResponse } from '../types/message'

export const SUPPORT_RESOURCES: Record<string, CommandResponse> = {
  // ============ 主選單 ============
  '#扶助資源': {
    type: 'cards',
    content: '需要幫忙嗎？讓我們來協助您！',
    cards: [
      {
        id: 'social-welfare',
        title: '💰 社福資源',
        description: '政府有很多資源可以提供唷~',
        links: [
          { text: '查看詳情', type: 'command', action: '#社福資源' }
        ]
      },
      {
        id: 'employment-resources',
        title: '💼 就業資源',
        description: '找工作不煩惱~來看看有什麼資源吧！',
        links: [
          { text: '查看詳情', type: 'command', action: '#就業資源' }
        ]
      },
      {
        id: 'medical-subsidy',
        title: '🏥 醫療補助',
        description: '醫療相關費用補助資訊',
        links: [
          { text: '查看詳情', type: 'command', action: '#醫療補助' }
        ]
      },
      {
        id: 'counseling-subsidy',
        title: '💭 心理諮商補助',
        description: '免費心理諮商輔導服務',
        links: [
          { text: '了解更多', type: 'command', action: '#心理諮商補助' }
        ]
      },
      {
        id: 'rehabilitation-support',
        title: '🔄 更生人扶助',
        description: '重新回歸社會的支持服務',
        links: [
          { text: '查看詳情', type: 'command', action: '#更生人扶助' }
        ]
      }
    ]
  },

  // ============ A. 社福資源 ============
  '#社福資源': {
    type: 'cards',
    content: '政府有很多資源可以提供唷~',
    cards: [
      {
        id: 'meal-voucher',
        title: '🍱 弱勢藥癮者暖心餐食券',
        description: '餐食兌換券可以協助您度過短期經濟困難的生活需求',
        links: [
          { text: '了解申請', type: 'command', action: '#弱勢藥癮者暖心餐食券' }
        ]
      },
      {
        id: 'food-bank',
        title: '🏪 實物銀行',
        description: '提供短期生活物資與民生用品',
        links: [
          { text: '查看詳情', type: 'command', action: '#實物銀行' }
        ]
      },
      {
        id: 'private-resources',
        title: '❤️ 民間物資及經濟補助單位',
        description: '民間有愛~讓我們一起度過難關',
        links: [
          { text: '查看單位', type: 'command', action: '#民間物資及經濟補助單位' }
        ]
      },
      {
        id: 'welfare-centers',
        title: '🏢 社會福利服務中心據點',
        description: '18處社會福利服務中心提供便捷服務',
        links: [
          { text: '了解更多', type: 'command', action: '#社會福利服務中心據點' }
        ]
      },
      {
        id: 'homeless-service',
        title: '🏠 街友中心服務',
        description: '提供街友安置、關懷、就業輔導等服務',
        links: [
          { text: '查看服務', type: 'command', action: '#街友中心服務' }
        ]
      }
    ]
  },

  '#弱勢藥癮者暖心餐食券': {
    type: 'cards',
    content: '餐食兌換券可以協助您度過短期經濟困難的生活需求',
    cards: [
      {
        id: 'eligibility',
        title: '📋 申請對象',
        description: '了解申請資格與條件',
        links: [
          { text: '查看資格', type: 'command', action: '#暖心餐食券申請對象' }
        ]
      },
      {
        id: 'application',
        title: '📝 申請方式',
        description: '了解如何申請暖心餐食券',
        links: [
          { text: '查看方式', type: 'command', action: '#暖心餐食券申請方式' }
        ]
      }
    ]
  },

  '#暖心餐食券申請對象': {
    type: 'rich-text',
    content: '弱勢藥癮者暖心餐食服務之服務對象',
    richContent: `
      <b>📋 弱勢藥癮者暖心餐食服務之服務對象</b><br><br>

      須設籍或實際居住在高雄市的藥癮個案符合下列條件之一，經輔導專業人員評估後，認定需要協助者。<br><br>

      <b>申請條件：</b><br>
      1. 經濟弱勢戶（邊緣戶、有急迫的經濟壓力、經濟陷入困境，三餐難以為繼者）。<br>
      2. 因非自願離職、緩起訴附命或其他原因無法工作<br>
      3. 家中主要生計者失業，生產人口少，依賴人口多。<br>
      4. 有突發狀況如受傷、疾病、住院、重大事故等。<br><br>

      🤝 <b>請與您的個管員聯繫，將很快協助安排喔！</b>
    `
  },

  '#暖心餐食券申請方式': {
    type: 'rich-text',
    content: '申請暖心餐食服務說明',
    richContent: `
      <b>📝 申請暖心餐食服務說明</b><br><br>

      由本局個管員或網絡單位評估其申請條件<br><br>

      🤝 <b>請與您的個管員聯繫，將很快協助安排喔！</b>
    `
  },

  '#實物銀行': {
    type: 'rich-text',
    content: '實物銀行服務',
    richContent: `
      <b>🏪 實物銀行</b><br><br>

      實物銀行可提供以下服務~幫助您度過生活難關💪<br><br>

      提供特定服務對象短期生活物資與民生用品，或提供食物券至合作之賣場領取熱食、生鮮食材等生活必需品(不得購買菸、酒等非生活必需品)，並受理各方善心物資與生活用品捐贈。<br><br>

      🤝 <b>請與您的個管員聯繫，將很快協助安排喔！</b>
    `
  },

  '#民間物資及經濟補助單位': {
    type: 'rich-text',
    content: '民間物資及經濟補助單位',
    richContent: `
      <b>❤️ 民間物資及經濟補助單位</b><br><br>

      民間有愛~讓我們一起度過難關❤️<br><br>

      <b>1. 中華基督教救助協會【1919食物銀行】</b><br>
      📞 專線：0800-20-1919<br>
      ✉️ 信箱：support@ccra.org.tw (來信提供所在縣巿/區及聯繫電話)<br>
      ⏰ 時間：週一至週五10點-17點<br><br>

      <b>2. 高雄勵馨基金會-高雄愛馨物資分享中心</b><br>
      📞 電話：(07)740-8595<br>
      🏢 地址：高雄市鳳山區建國路二段169號<br>
      ⏰ 營業時間：週一至週五 10:00-17:00<br><br>

      <b>3. 財團法人佛教慈濟慈善事業基金會【高雄分會】</b><br>
      📞 電話：07-3987667(請總機轉接社服組)<br>
      🏢 地址：高雄市三民區河堤南路50號<br><br>

      <b>4. 財團法人全聯慶祥慈善事業基金會</b><br>
      📞 電話：(07)7405-725<br>
      ✉️ 申請網站：<a href="https://www.pxmart.org.tw" target="_blank">點我申請</a><br><br>

      <b>5. 中華基督教救助協會【1919急難家庭】</b><br>
      免付費專線：0800-20-1919<br>
      <b>【高屏區辦事處】</b>(高雄市、屏東縣、澎湖縣)<br>
      📞 電話：(07)380-3755<br>
      ⏰ 時間：週一至週五 10:00-17:00<br><br>

      🤝 <b>請與您的個管員聯繫，將很快協助安排喔！</b>
    `
  },

  '#社會福利服務中心據點': {
    type: 'cards',
    content: '社會福利服務中心提供多元服務',
    cards: [
      {
        id: 'welfare-center',
        title: '🏢 社會福利服務中心據點',
        description: '18處中心提供脆弱家庭服務及福利申請',
        links: [
          { text: '了解更多', type: 'command', action: '#社會福利服務中心據點資訊' }
        ]
      },
      {
        id: 'parent-child',
        title: '👨‍👩‍👧‍👦 親子館服務據點',
        description: '0-6歲兒童及家長育兒資源服務',
        links: [
          { text: '查看詳情', type: 'command', action: '#親子館服務據點' }
        ]
      },
      {
        id: 'early-intervention',
        title: '👶 兒童早療服務據點',
        description: '發展遲緩幼兒的專業介入服務',
        links: [
          { text: '了解服務', type: 'command', action: '#兒童早療服務據點' }
        ]
      }
    ]
  },

  '#社會福利服務中心據點資訊': {
    type: 'rich-text',
    content: '高雄市社會福利服務中心據點',
    richContent: `
      <b>🏢 高雄市社會福利服務中心據點</b><br><br>

      為提供民眾更便捷的福利申請及服務，高雄市政府社會局共設置18處社會福利服務中心，辦理脆弱家庭服務及受理民眾申請之福利項目，將民眾經常性申辦的福利服務窗口，延伸設置到各社會福利服務中心，落實福利社區化。💪<br><br>

      ✅ <b>服務內容：</b><br>
      1. 脆弱家庭服務：提供脆弱家庭預防處遇及個案管理服務。<br>
      2. 資源運用：協助媒合及運用社會福利資源；彙集民間慈善民生物資設置物資站。<br>
      3. 諮詢服務：提供社會福利服務相關業務之內容及運用諮詢服務。<br>
      4. 舉辦社區性活動：舉辦促進社會功能之文康、親職、輔導、研習及宣導活動等。<br>
      5. 設施設備使用服務：各中心依其空間大小分別設置聯誼室、體能區、多功能教室及會談室等空間並提供書報、文康用品等休閒設施供民眾使用。<br><br>

      👉 <b>詳細資訊請參考：</b><br>
      <a href="https://socbu.kcg.gov.tw/index.php?prog=2&b_id=12&m_id=283&s_id=1605" target="_blank">點我查看</a><br><br>

      🤝 <b>請與您的個管員聯繫，將很快協助喔！</b>
    `
  },

  '#親子館服務據點': {
    type: 'rich-text',
    content: '高雄親子館服務據點',
    richContent: `
      <b>👨‍👩‍👧‍👦 高雄親子館服務據點</b><br><br>

      親子館提供0-6歲兒童及其家長育兒資源服務，依不同年齡層嬰幼兒規劃活動區域，提供豐富的玩具、繪本及圖書，促進學齡前兒童智能及大小肌肉等發展。同時也提供托育與照顧諮詢服務，並規劃親職課程與親子活動。👨‍👩‍👧‍👦<br><br>

      👉 <b>詳細資訊請參考：</b><br>
      <a href="https://cwsc.kcg.gov.tw/cp.aspx?n=FB81D67DDCEA0CF0" target="_blank">點我查看</a><br><br>

      🤝 <b>請與您的個管員聯繫，將很快協助安排喔！</b>
    `
  },

  '#兒童早療服務據點': {
    type: 'rich-text',
    content: '高雄市早期療育服務據點',
    richContent: `
      <b>👶 高雄市早期療育服務據點</b><br><br>

      早療(早期療育)主要是對於發展遲緩或有發展障礙風險的幼兒所提供的專業介入服務。主要目的是在孩子大腦發展最快速的早期階段（通常是0-6歲），及時提供適當的刺激和訓練，以促進兒童各方面的發展~<br><br>

      👉 <b>詳細資訊請參考：</b><br>
      <a href="https://cwsc.kcg.gov.tw/cp.aspx?n=9CB4447DC38A0F8F" target="_blank">點我查看</a><br><br>

      🤝 <b>請與您的個管員聯繫，將很快協助喔！</b>
    `
  },

  '#街友中心服務': {
    type: 'rich-text',
    content: '街友中心服務',
    richContent: `
      <b>🏠 街友中心服務</b><br><br>

      街友中心可提供以下的服務<br><br>

      ✅ <b>服務內容：</b><br><br>

      <b>1. 街友安置</b><br>
      提供生活照顧、家屬協尋、協助返家、轉介安置、媒合就業、協助就醫等<br><br>

      <b>2. 街友外展關懷活動</b><br>
      提供義診、義剪、沐浴、禦寒衣物及餐食服務<br><br>

      <b>3. 短期住宿旅館服務</b><br>
      為使颱風及寒流等惡劣氣候來襲時，能讓每位街友都能即時獲得照顧，提供緊急安置服務。<br><br>

      <b>4. 就業輔導服務</b><br>
      結合民間與勞政資源，提供街友職業諮詢與媒合，協助街友自立重返社區。<br><br>

      📌 <b>服務據點：</b><br><br>

      <b>1. 三民街友服務中心－惜緣居</b><br>
      🏢 地址：高雄市三民區天祥二路31號<br>
      📞 聯絡方式：07-3432263<br><br>

      <b>2. 鳳山街友服務中心－慈心園</b><br>
      🏢 地址：高雄市鳳山區博愛路477巷18號<br>
      📞 聯絡方式：07-7190895<br><br>

      🤝 <b>請與您的個管員聯繫，將很快協助安排喔！</b>
    `
  },

  // ============ B. 就業資源 ============
  '#就業資源': {
    type: 'cards',
    content: '找工作不煩惱~來看看有什麼資源吧！',
    cards: [
      {
        id: 'employment-service',
        title: '🏢 就業服務站',
        description: '高雄市各區就業服務站資訊',
        links: [
          { text: '查看詳情', type: 'command', action: '#就業服務站' }
        ]
      },
      {
        id: 'skill-training',
        title: '💪 職能培力服務',
        description: '多元活動和培訓，幫助發掘興趣、規劃職涯',
        links: [
          { text: '了解更多', type: 'command', action: '#職能培力服務' }
        ]
      },
      {
        id: 'work-reward',
        title: '🏆 職得獎勵方案',
        description: '鼓勵參與職能培力，提升就業準備',
        links: [
          { text: '查看方案', type: 'command', action: '#職得獎勵方案' }
        ]
      }
    ]
  },

  // 就業資源的子項目（與多元輔導共用相同內容）
  '#就業服務站': {
    type: 'rich-text',
    content: '就業服務站資訊',
    richContent: `
      <b>🏢 就業服務站</b><br><br>

      您可到以下單位進行就業服務的資訊洽詢喔！<br><br>

      <b>1. 高雄市政府勞工局訓練就業中心</b><br>
      📞 電話：(07)733-0823～28<br>
      🏢 地址：833 高雄市鳥松區大埤路117號<br>
      ⏰ 服務時間：週一至週五上午08:00 ~12:00/下午01:30 ~ 05:30<br><br>

      <b>2. 高雄市政府勞工局訓練就業中心 - 大寮場域</b><br>
      📞 電話：(07)783-5011轉132~134<br>
      🏢 地址：831高雄市大寮區捷西路300號<br>
      ⏰ 服務時間：週一至週五上午08:00 ~12:00/下午01:30 ~ 05:30<br><br>

      <b>3. 高雄市各區域就業服務站</b><br>
      👉 各服務站詳細資訊請參考：<br>
      <a href="https://ktec.kcg.gov.tw/cp.aspx?n=AEE9FAB4703BAE6D" target="_blank">點我查看</a><br><br>

      🤝 <b>請與您的個管員聯繫，將很快協助安排喔！</b>
    `
  },

  '#職能培力服務': {
    type: 'rich-text',
    content: '職能培力服務',
    richContent: `
      <b>💪 職能培力服務</b><br><br>

      職能培力服務透過多元活動和培訓，幫助個人發掘興趣、規劃職涯、獲得技能認證，致力於協助藥癮個案回歸社會。<br><br>

      以下是服務單位的介紹~<br><br>

      <b>【米迦勒社會福利協會】</b><br>
      🏢 單位地址：高雄市三民區民族一路88-2號B室<br>
      📞 單位電話：(07)370-3573<br><br>

      ✅ <b>服務內容：</b><br>
      • 提供開放式定點服務，提興趣探索、職涯規劃、職業體驗活動。<br>
      • 辦理技能訓練、輔導證照考試、安排職場見(實)習。<br>
      • 開發藥癮個案社會復歸友善職場。<br><br>

      🤝 <b>請與您的個管員聯繫，將很快協助安排喔！</b>
    `
  },

  '#職得獎勵方案': {
    type: 'mixed',
    content: '職得獎勵方案',
    richContent: `
      <b>🏆 職得獎勵方案</b><br><br>

      這個方案鼓勵藥癮個案參與職能培力及技能培訓，提升就業準備，協助藥癮個案穩定就業與改善經濟，找到正向生活重心，促進順利復歸社會。<br><br>

      ➡️ <b>方案內容：</b><br><br>

      🔹 <b>就業加值金：</b><br>
      • 部分工時且每月工作60小時者，一年最高補助15,000元<br>
      • 每月計酬全職工作者及自行創業者，一年最高補助28,500元<br><br>

      🔹 <b>職業訓練助學金：</b><br>
      • 經公立就業服務機構參訓或經職訓單位錄取，結訓後得申請助學金<br>
      • 一年最高補助8,000元<br><br>

      🔹 <b>技能檢定報名費補助：</b><br>
      • 專業證照檢定(報名費、檢定費、材料費等)<br>
      • 一年最高補助5,000元<br><br>

      👉 <b>詳細資訊請參考：</b><br>
      <a href="https://dsacp.kcg.gov.tw/Content_List.aspx?n=07AF11C9B6C7DA16" target="_blank">點我查看</a><br><br>

      🤝 <b>請與您的個管員聯繫，將很快協助安排喔！</b>
    `,
    images: [
      {
        url: '/src/assets/gov_images/職得獎勵~就業支持方案.png',
        alt: '職得獎勵~就業支持方案',
        caption: '職得獎勵，支持您的就業之路'
      }
    ]
  },

  // ============ C. 醫療補助 ============
  '#醫療補助': {
    type: 'cards',
    content: '醫療相關費用補助資訊',
    cards: [
      {
        id: 'reproductive-health',
        title: '👶 生育保健醫療支持補助',
        description: '藥癮個案生育保健醫療支持補助',
        links: [
          { text: '了解更多', type: 'command', action: '#生育保健醫療支持補助' }
        ]
      },
      {
        id: 'hospitalization-subsidy',
        title: '🏥 戒癮住院治療費用補助',
        description: '減輕您住院的負擔',
        links: [
          { text: '查看詳情', type: 'command', action: '#戒癮住院治療費用補助' }
        ]
      },
      {
        id: 'partner-hospitals',
        title: '🏥 住院治療補助合作醫院',
        description: '藥癮個案住院治療費用補助合作醫院',
        links: [
          { text: '查看名單', type: 'command', action: '#住院治療補助合作醫院' }
        ]
      }
    ]
  },

  '#生育保健醫療支持補助': {
    type: 'mixed',
    content: '藥癮個案生育保健醫療支持補助',
    richContent: `
      <b>👶 藥癮個案生育保健醫療支持補助</b><br><br>

      ✅ <b>補助項目：</b><br>
      • 子宮內避孕器裝置費用<br>
      • 門診看診費<br>
      • 診斷性評估費<br>
      • 高層次超音波費用<br>
      • 早產風險篩檢<br>
      • 新生兒篩檢<br>
      • 新生兒加護病房費用<br>
      • 中止妊娠費用<br>
      • 女性結紮手術費用<br>
      • 男性結紮手術費用<br>
      • 手術麻醉費用<br>
      • 醫療雜項支出等<br><br>

      👉 <b>詳細資訊請參考：</b><br>
      <a href="https://dsacp.kcg.gov.tw/Content_List.aspx?n=2D15369E2D6450E8" target="_blank">點我查看</a><br><br>

      🤝 <b>請洽詢醫院或您的個管員，將很快協助安排喔！</b>
    `,
    images: [
      {
        url: '/src/assets/gov_images/婦幼優生保健補助.png',
        alt: '婦幼優生保健補助',
        caption: '婦幼優生保健補助資訊'
      }
    ]
  },

  '#戒癮住院治療費用補助': {
    type: 'mixed',
    content: '戒癮住院治療費用補助',
    richContent: `
      <b>🏥 戒癮住院治療費用補助</b><br><br>

      高雄市政府對於藥癮個案住院治療的費用有提供補助喔！減輕您住院的負擔~<br><br>

      <b>補助包含：</b><br>
      • 病房費<br>
      • 住院診察費<br>
      • 藥事服務費<br>
      • 檢驗費<br>
      • 檢查費<br>
      • 精神科治療費<br>
      • 護理費<br>
      • 處置費<br>
      • 材料費等<br><br>

      👉 <b>詳細資訊請參考：</b><br>
      <a href="https://dsacp.kcg.gov.tw/Content_List.aspx?n=963039E18037CE25" target="_blank">點我查看</a><br><br>

      🤝 <b>請與您的個管員聯繫，將很快協助安排喔！</b>
    `,
    images: [
      {
        url: '/src/assets/gov_images/少年醫療戒治補助.png',
        alt: '少年醫療戒治補助',
        caption: '少年醫療戒治補助說明'
      },
      {
        url: '/src/assets/gov_images/藥癮治療補助.png',
        alt: '藥癮治療補助',
        caption: '藥癮治療補助資訊'
      },
      {
        url: '/src/assets/gov_images/高雄市藥癮治療機構一覽表.png',
        alt: '高雄市藥癮治療機構一覽表',
        caption: '高雄市藥癮治療機構一覽表'
      }
    ]
  },

  '#住院治療補助合作醫院': {
    type: 'rich-text',
    content: '藥癮個案住院治療費用補助_合作醫院',
    richContent: `
      <b>🏥 藥癮個案住院治療費用補助_合作醫院</b><br><br>

      1. 財團法人私立高雄醫學大學附設中和紀念醫院<br>
      2. 高雄市立凱旋醫院<br>
      3. 國軍高雄總醫院附設民眾診療服務處<br>
      4. 財團法人台灣省私立高雄仁愛之家附設慈惠醫院<br>
      5. 義大醫療財團法人義大醫院<br>
      6. 長庚醫療財團法人高雄長庚紀念醫院<br>
      7. 衛生福利部旗山醫院<br>
      8. 國軍左營總醫院<br><br>

      🤝 <b>請與您的個管員聯繫，將很快協助安排喔！</b>
    `
  },

  // ============ D. 心理諮商補助 ============
  '#心理諮商補助': {
    type: 'rich-text',
    content: '藥癮個案家庭心理諮商輔導計畫',
    richContent: `
      <b>💭 藥癮個案家庭心理諮商輔導計畫</b><br><br>

      高雄市政府目前有針對藥癮個案及其家人的免費心理諮商輔導計畫。<br><br>

      您可以獲得個人、家庭或團體諮商服務。<br>
      每年最多可以獲得12次免費服務，具體次數會根據您的需求評估。<br><br>

      👉 <b>詳細資訊請參考：</b><br>
      <a href="https://dsacp.kcg.gov.tw/Content_List.aspx?n=B9E9D2CB6116C3D2" target="_blank">點我查看</a><br><br>

      🤝 <b>請與您的個管員聯繫，將很快協助安排喔！</b>
    `
  },

  // ============ E. 更生人扶助 ============
  '#更生人扶助': {
    type: 'rich-text',
    content: '更生人扶助服務',
    richContent: `
      <b>🔄 更生人扶助</b><br><br>

      重新回歸社會不用擔心~💪<br><br>

      更生人扶助提供更生人技能檢定補助、輔導就業、就學、急難救助、經濟扶助、資助更生人醫藥費用、創業貸款、心理諮商等服務，可以參考以下單位~<br><br>

      <b>1. 臺灣更生保護會</b><br><br>

      <b>【高雄分會】</b><br>
      📞 電話：(07)216-1468轉3806、3807<br>
      🏢 地址：高雄市前金區中正四路249號1樓<br><br>

      <b>【橋頭分會】</b><br>
      📞 電話：(07)612-8177<br>
      🏢 地址：高雄市橋頭區經武路868號<br><br>

      <b>2. 財團法人高雄市毒品防制事務基金會</b><br><br>

      🤝 <b>請與您的個管員聯繫，將很快協助安排喔！</b>
    `
  }
}