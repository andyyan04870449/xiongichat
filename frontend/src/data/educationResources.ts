// 衛教資源的詳細資料
import { CommandResponse } from '../types/message'

export const EDUCATION_RESOURCES: Record<string, CommandResponse> = {
  // ============ 主選單 ============
  '#衛教資源': {
    type: 'cards',
    content: '請選擇您需要的衛教資源類別：',
    cards: [
      {
        id: 'legal-aid',
        title: '⚖️ 法律扶助',
        description: '提供法律諮詢、法律扶助基金會資訊等法律相關協助',
        links: [
          { text: '查看詳情', type: 'command', action: '#法律扶助' }
        ]
      },
      {
        id: 'aids-education',
        title: '🎗️ 愛滋衛教',
        description: '愛滋病預防、治療與相關衛教資訊',
        links: [
          { text: '查看詳情', type: 'command', action: '#愛滋衛教' }
        ]
      },
      {
        id: 'maternal-child',
        title: '👶 婦幼衛教',
        description: '母嬰照護、生育保健、婦幼醫療補助等服務',
        links: [
          { text: '查看詳情', type: 'command', action: '#婦幼衛教' }
        ]
      },
      {
        id: 'addiction-treatment',
        title: '💊 戒癮衛教',
        description: '戒癮資源、中途之家、心理諮商、醫療補助等服務',
        links: [
          { text: '查看詳情', type: 'command', action: '#戒癮衛教' }
        ]
      }
    ]
  },

  // ============ 法律扶助 ============
  '#法律扶助': {
    type: 'rich-text',
    content: '法律扶助資源',
    richContent: `
      <b>⚖️ 法律扶助資源</b><br><br>

      如果您需要法律相關的協助，可參考以下機構：<br><br>

      <b>1. 財團法人法律扶助基金會</b><br><br>

      <b>【高雄分會】</b><br>
      🏢 地址：高雄市新興區中正三路25號6樓<br>
      📞 電話：(07)222-2360<br>
      👉 線上預約：<a href="https://legal-advice.laf.org.tw/" target="_blank">點我預約</a><br>
      ✅ 提供「法律諮詢」及「申請扶助律師」服務<br><br>

      <b>【橋頭分會】</b><br>
      🏢 地址：高雄市橋頭區經武路2號2樓<br>
      📞 電話：(07)612-1137<br>
      👉 線上預約：<a href="https://legal-advice.laf.org.tw/" target="_blank">點我預約</a><br>
      ✅ 提供「法律諮詢」及「申請扶助律師」服務<br><br>

      <b>2. 高雄市政府免費法律諮詢</b><br><br>

      🏢 聯絡單位：<br>
      • 四維行政中心<br>
      • 高雄市新住民會館<br>
      • 區公所（鳳山、岡山、旗山、前鎮、旗津、林園）<br>
      ✅ 提供免費法律諮詢服務<br><br>

      💡 <b>小提醒：請準備相關文件資料，以利律師了解您的狀況</b>
    `
  },

  // ============ 愛滋衛教 ============
  '#愛滋衛教': {
    type: 'rich-text',
    content: '愛滋病防治衛教',
    richContent: `
      <b>🎗️ 愛滋衛教</b><br><br>

      <b>避免被傳染愛滋病的方法：</b><br><br>

      (1) 絕對不要重複使用或與別人共用針頭、針筒、稀釋液或其他準備藥物之容器。<br><br>

      (2) 固定性伴侶，若與他人有性行為或性接觸時，請記得一定要戴上保險套，以保護自己及他人，避免感染愛滋病毒。<br><br>

      想了解更多關於愛滋病衛教資訊可以到各區衛生所諮詢唷！
    `
  },

  // ============ 婦幼衛教主選單 ============
  '#婦幼衛教': {
    type: 'cards',
    content: '請選擇您需要的婦幼衛教服務：',
    cards: [
      {
        id: 'maternal-care',
        title: '👶 母嬰照護',
        description: '母嬰照護指引、孕期到產後的完整照護資訊',
        links: [
          { text: '了解更多', type: 'command', action: '#母嬰照護' }
        ]
      },
      {
        id: 'reproductive-health',
        title: '🏥 生育保健',
        description: '生育保健醫療支持補助、避孕措施等資訊',
        links: [
          { text: '了解更多', type: 'command', action: '#生育保健' }
        ]
      },
      {
        id: 'medical-subsidy',
        title: '💰 婦幼醫療補助',
        description: '各項婦幼相關醫療費用補助資訊',
        links: [
          { text: '了解更多', type: 'command', action: '#婦幼醫療補助' }
        ]
      },
      {
        id: 'counseling-program',
        title: '👥 輔導方案',
        description: '女性藥癮個案支持團體、輔導服務',
        links: [
          { text: '了解更多', type: 'command', action: '#輔導方案' }
        ]
      },
      {
        id: 'menstrual-equity',
        title: '🌸 月經平權',
        description: '月經平權政策、生理用品支持服務',
        links: [
          { text: '了解更多', type: 'command', action: '#月經平權' }
        ]
      }
    ]
  },

  // ============ 婦幼衛教子項目 ============
  '#母嬰照護': {
    type: 'images',
    content: '母嬰照護 - 陪你同行，孕釀希望❤️',
    images: [
      {
        url: '/src/assets/gov_images/女生藥物濫用原因.png',
        alt: '女生藥物濫用原因',
        caption: '了解藥物濫用的原因'
      },
      {
        url: '/src/assets/gov_images/孕前到產後每階段要注意的事.png',
        alt: '孕前到產後注意事項',
        caption: '孕期各階段重要提醒'
      },
      {
        url: '/src/assets/gov_images/陪妳同行.png',
        alt: '陪妳同行',
        caption: '我們與您同在'
      },
      {
        url: '/src/assets/gov_images/藥物濫用對孕婦及胎兒影響.png',
        alt: '藥物濫用影響',
        caption: '保護母嬰健康'
      }
    ]
  },

  '#生育保健': {
    type: 'rich-text',
    content: '生育保健醫療支持',
    richContent: `
      <b>🏥 藥癮個案生育保健醫療支持補助</b><br><br>

      <b>✅ 補助項目：</b><br>
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

      👉 <b>詳細資訊：</b><br>
      <a href="https://dsacp.kcg.gov.tw/Content_List.aspx?n=2D15369E2D6450E8" target="_blank">點我查看完整補助資訊</a><br><br>

      🤝 <b>請洽詢醫院或您的個管員，將很快協助安排喔！</b>
    `
  },

  '#婦幼醫療補助': {
    type: 'rich-text',
    content: '婦幼醫療補助資訊',
    richContent: `
      <b>💰 婦幼醫療補助</b><br><br>

      同「衛教資源-戒癮衛教-戒癮資源補助」
    `
  },

  '#輔導方案': {
    type: 'rich-text',
    content: '女性支持輔導方案',
    richContent: `
      <b>👥 女性藥癮個案支持團體</b><br><br>

      主要為幫助女性藥癮個案重拾健康、快樂的生活。透過團體的力量、定期性的活動，改善女性藥癮個案經濟、情感、人際關係、生育及家庭等5面向常見問題，促進身心健康安全~❤️<br><br>

      🤝 <b>請與您的個管員聯繫，將很快協助安排喔！</b>
    `
  },

  '#月經平權': {
    type: 'mixed',
    content: '月經平權政策說明',
    richContent: `
      <b>🌸 月經平權</b><br><br>

      <b>什麼是月經平權？</b><br>
      月經平權是指消除在保健方面對婦女的歧視，在性別平等的基礎上取得各種包括有關計劃生育的保健服務。❤️<br><br>

      <b>毒防局服務內容：</b><br>
      推動月經平權暨提升藥癮個案生育保健知能<br><br>

      <b>服務對象：</b><br>
      符合設籍或實際居住高雄市列管中之15-49歲育齡婦女藥癮個案<br><br>

      <b>服務方式：</b><br>
      • 個管員進行家庭訪視<br>
      • 提供月事所需相關物品<br>
      • 依個案需求，提供個別用藥、生育保健相關討論<br>
    `,
    images: [
      {
        url: '/src/assets/gov_images/月經平權.png',
        alt: '月經平權',
        caption: '月經平權政策說明'
      },
      {
        url: '/src/assets/gov_images/避孕措施有哪些.png',
        alt: '避孕措施',
        caption: '各種避孕措施介紹'
      }
    ]
  },

  // ============ 戒癮衛教主選單 ============
  '#戒癮衛教': {
    type: 'cards',
    content: '請選擇您需要的戒癮衛教服務：',
    cards: [
      {
        id: 'halfway-house',
        title: '🏠 中途之家服務',
        description: '提供中短期安置服務與生活重建',
        links: [
          { text: '查看詳情', type: 'command', action: '#中途之家' }
        ]
      },
      {
        id: 'counseling-service',
        title: '💭 心理諮商服務',
        description: '專業心理諮商與輔導服務',
        links: [
          { text: '查看詳情', type: 'command', action: '#心理諮商' }
        ]
      },
      {
        id: 'treatment-institution',
        title: '🏥 指定戒治機構',
        description: '藥癮戒治及替代治療機構資訊',
        links: [
          { text: '查看詳情', type: 'command', action: '#戒治機構' }
        ]
      },
      {
        id: 'treatment-subsidy',
        title: '💰 戒癮資源補助',
        description: '各項戒癮治療費用補助資訊',
        links: [
          { text: '查看詳情', type: 'command', action: '#戒癮資源補助' }
        ]
      }
    ]
  },

  // ============ 戒癮衛教子項目 ============
  '#中途之家': {
    type: 'rich-text',
    content: '中途之家服務資訊',
    richContent: `
      <b>🏠 中途之家服務</b><br><br>

      <b>服務對象：</b><br>
      出監或返家困難、無家可歸且有心想要改變的藥癮個案<br><br>

      <b>服務內容：</b><br>
      提供中短期的安置服務與生活重建，包含：<br>
      • 心理輔導<br>
      • 戒癮治療<br>
      • 諮商輔導<br>
      • 職能培訓<br>
      • 就業協助<br>
      • 離園準備<br><br>

      <b>合作機構：</b><br><br>

      <b>1. 財團法人基督教晨曦會</b><br>
      📞 電話：(02)2231-7744<br><br>

      <b>2. 財團法人屏東縣私立基督教沐恩之家</b><br>
      📞 電話：(07)723-0595<br><br>

      <b>3. 愛鄰舍更生家園-高雄輔導所</b><br>
      📞 電話：(07)787-7547<br>
      📱 手機：0919-993-840<br><br>

      <b>4. 渡安居中途之家</b><br>
      📞 電話：(03)933-2073<br><br>

      <b>5. 社團法人台灣露德協會</b><br>
      📞 電話：04-25943223<br>
      📱 手機：0928-712263<br><br>

      <b>6. 財團法人利伯他茲教育基金會</b><br>
      📞 電話：02-29363201轉41<br><br>

      🤝 <b>請與您的個管員聯繫，將很快協助安排喔！</b>
    `
  },

  '#心理諮商': {
    type: 'rich-text',
    content: '心理諮商服務',
    richContent: `
      <b>💭 心理諮商服務</b><br><br>

      （相關服務資訊請洽詢個管員）
    `
  },

  '#戒治機構': {
    type: 'mixed',
    content: '高雄市指定藥癮戒治及替代治療機構',
    richContent: `
      <b>🏥 高雄市指定藥癮戒治及替代治療機構</b><br><br>

      <b>請勇敢尋求幫助！</b><br>
      照顧好自己的身體，是最重要的事情~<br>
      一般疾病或是戒癮療程，透過專業治療和關愛支持，能助您重拾健康生活~💪<br><br>

      <b>詳細機構名單：</b><br>
      👉 <a href="#" target="_blank">高雄市指定藥癮戒治機構</a><br>
      👉 <a href="#" target="_blank">高雄市替代治療執行機構(含美沙冬衛星給藥點)</a><br><br>

      🤝 <b>請洽詢醫院或您的個管員，將很快協助安排喔！</b>
    `,
    images: [
      {
        url: '/src/assets/gov_images/高雄市藥癮治療機構一覽表.png',
        alt: '高雄市藥癮治療機構',
        caption: '高雄市藥癮治療機構一覽表'
      }
    ]
  },

  '#戒癮資源補助': {
    type: 'cards',
    content: '戒癮資源補助項目：',
    cards: [
      {
        id: 'counseling-subsidy',
        title: '💭 心理諮商輔導補助',
        description: '藥癮個案家庭心理諮商輔導計畫',
        links: [
          { text: '了解更多', type: 'command', action: '#心理諮商輔導補助' }
        ]
      },
      {
        id: 'reproductive-subsidy',
        title: '👶 藥癮個案生育保健醫療支持補助',
        description: '藥癮個案生育保健醫療支持補助',
        links: [
          { text: '了解更多', type: 'command', action: '#藥癮個案生育保健醫療支持補助' }
        ]
      },
      {
        id: 'hospitalization-subsidy',
        title: '🏥 戒癮住院治療費用補助',
        description: '戒癮住院治療費用補助',
        links: [
          { text: '了解更多', type: 'command', action: '#戒癮住院治療費用補助' }
        ]
      },
      {
        id: 'partner-hospitals',
        title: '🏥 住院治療費用補助合作醫院',
        description: '藥癮個案住院治療費用補助_合作醫院',
        links: [
          { text: '查看名單', type: 'command', action: '#住院治療費用補助合作醫院' }
        ]
      }
    ]
  },

  '#心理諮商輔導補助': {
    type: 'rich-text',
    content: '心理諮商輔導補助詳情',
    richContent: `
      <b>💭 藥癮個案家庭心理諮商輔導計畫</b><br><br>

      高雄市政府目前有針對藥癮個案及其家人的免費心理諮商輔導計畫。<br><br>

      <b>服務內容：</b><br>
      • 個人諮商服務<br>
      • 家庭諮商服務<br>
      • 團體諮商服務<br><br>

      <b>補助額度：</b><br>
      每年最多可以獲得12次免費服務，具體次數會根據您的需求評估。<br><br>

      👉 <b>詳細資訊請參考：</b><br>
      <a href="https://dsacp.kcg.gov.tw/Content_List.aspx?n=B9E9D2CB6116C3D2" target="_blank">點我查看完整資訊</a><br><br>

      🤝 <b>請與您的個管員聯繫，將很快協助安排喔！</b>
    `
  },

  '#藥癮個案生育保健醫療支持補助': {
    type: 'mixed',
    content: '生育保健醫療支持補助',
    richContent: `
      <b>👶 藥癮個案生育保健醫療支持補助</b><br><br>

      <b>✅ 補助項目：</b><br>
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
      <a href="https://dsacp.kcg.gov.tw/Content_List.aspx?n=2D15369E2D6450E8" target="_blank">點我查看完整資訊</a><br><br>

      🤝 <b>請洽詢醫院或您的個管員，將很快協助安排喔！</b>
    `,
    images: [
      {
        url: '/src/assets/gov_images/婦幼優生保健補助.png',
        alt: '婦幼優生保健補助',
        caption: '婦幼優生保健補助說明'
      }
    ]
  },

  '#戒癮住院治療費用補助': {
    type: 'mixed',
    content: '戒癮住院治療費用補助',
    richContent: `
      <b>🏥 戒癮住院治療費用補助</b><br><br>

      高雄市政府對於藥癮個案住院治療的費用有提供補助喔！減輕您住院的負擔~<br><br>

      <b>補助項目包含：</b><br>
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
      <a href="https://dsacp.kcg.gov.tw/Content_List.aspx?n=963039E18037CE25" target="_blank">點我查看完整資訊</a><br><br>

      🤝 <b>請與您的個管員聯繫，將很快協助安排喔！</b>
    `,
    images: [
      {
        url: '/src/assets/gov_images/少年醫療戒治補助.png',
        alt: '少年醫療戒治補助',
        caption: '少年醫療戒治補助說明'
      },
      {
        url: '/src/assets/gov_images/前言.png',
        alt: '補助前言',
        caption: '補助計畫說明'
      }
    ]
  },

  '#住院治療費用補助合作醫院': {
    type: 'rich-text',
    content: '住院治療費用補助合作醫院',
    richContent: `
      <b>🏥 藥癮個案住院治療費用補助_合作醫院</b><br><br>

      <b>合作醫院名單：</b><br><br>

      1. <b>財團法人私立高雄醫學大學附設中和紀念醫院</b><br><br>

      2. <b>高雄市立凱旋醫院</b><br><br>

      3. <b>國軍高雄總醫院附設民眾診療服務處</b><br><br>

      4. <b>財團法人台灣省私立高雄仁愛之家附設慈惠醫院</b><br><br>

      5. <b>義大醫療財團法人義大醫院</b><br><br>

      6. <b>長庚醫療財團法人高雄長庚紀念醫院</b><br><br>

      7. <b>衛生福利部旗山醫院</b><br><br>

      8. <b>國軍左營總醫院</b><br><br>

      🤝 <b>請與您的個管員聯繫，將很快協助安排喔！</b>
    `
  }
}