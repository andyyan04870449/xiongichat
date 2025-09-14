// 戒癮專區的詳細資料
import { CommandResponse } from '../types/message'

export const ADDICTION_RESOURCES: Record<string, CommandResponse> = {
  // ============ 主選單 ============
  '#戒癮專區': {
    type: 'cards',
    content: '您好，今天想要了解什麼資訊呢？',
    cards: [
      {
        id: 'halfway-house',
        title: '🏠 中途之家服務',
        description: '提供出監或返家困難、無家可歸且有心想要改變的藥癮個案中短期的安置服務與生活重建',
        links: [
          { text: '查看詳情', type: 'command', action: '#中途之家服務' }
        ]
      },
      {
        id: 'counseling-service',
        title: '💭 心理諮商服務',
        description: '如需預約心理諮商服務~請洽個管員協助喔！',
        links: [
          { text: '查看詳情', type: 'command', action: '#心理諮商服務' }
        ]
      },
      {
        id: 'treatment-institutions',
        title: '🏥 指定藥癮戒治及替代治療機構',
        description: '高雄市指定藥癮戒治及替代治療機構資訊',
        links: [
          { text: '查看詳情', type: 'command', action: '#指定藥癮戒治及替代治療機構' }
        ]
      },
      {
        id: 'addiction-subsidy',
        title: '💰 戒癮資源補助',
        description: '戒癮雖辛苦~讓我們來當您的後盾！',
        links: [
          { text: '查看詳情', type: 'command', action: '#戒癮資源補助' }
        ]
      }
    ]
  },

  // ============ A. 中途之家服務 ============
  '#中途之家服務': {
    type: 'rich-text',
    content: '中途之家服務',
    richContent: `
      <b>🏠 中途之家服務</b><br><br>

      中途之家提供~ 出監或返家困難、無家可歸且有心想要改變的藥癮個案中短期的安置服務與生活重建，其中包含心理輔導，戒癮治療、諮商輔導、職能培訓、就業協助以及離園準備等。<br><br>

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

  // ============ B. 心理諮商服務 ============
  '#心理諮商服務': {
    type: 'cards',
    content: '如需預約心理諮商服務~請洽個管員協助喔！',
    cards: [
      {
        id: 'lingya-counseling',
        title: '🏥 苓雅區-心理諮商機構',
        description: '凱旋醫院、禾好心理治療所、旅行心理治療所',
        links: [
          { text: '查看詳情', type: 'command', action: '#苓雅區心理諮商機構' }
        ]
      },
      {
        id: 'zuoying-counseling',
        title: '🏥 左營區-心理諮商機構',
        description: '耕心療癒診所、欣寧心理治療所',
        links: [
          { text: '查看詳情', type: 'command', action: '#左營區心理諮商機構' }
        ]
      },
      {
        id: 'fengshan-counseling',
        title: '🏥 鳳山區-心理諮商機構',
        description: '宇智心理治療所、路以心理治療所',
        links: [
          { text: '查看詳情', type: 'command', action: '#鳳山區心理諮商機構' }
        ]
      },
      {
        id: 'daliao-counseling',
        title: '🏥 大寮區-心理諮商機構',
        description: '高雄仁愛之家',
        links: [
          { text: '查看詳情', type: 'command', action: '#大寮區心理諮商機構' }
        ]
      }
    ]
  },

  '#苓雅區心理諮商機構': {
    type: 'rich-text',
    content: '苓雅區心理諮商機構',
    richContent: `
      <b>🏥 苓雅區心理諮商機構</b><br><br>

      <b>(1) 凱旋醫院</b><br>
      諮詢地點：高雄市立凱旋醫院<br>
      聯絡地址：高雄市苓雅區凱旋二路130號<br>
      🤝 請與您的個管員聯繫，將很快協助安排喔！<br><br>

      <b>(2) 禾好心理治療所</b><br>
      諮詢地點：禾好心理治療所<br>
      聯絡地址：高雄市苓雅區正大路119號2樓<br>
      🤝 請與您的個管員聯繫，將很快協助安排喔！<br><br>

      <b>(3) 旅行心理治療所</b><br>
      諮詢地點：旅行心理治療所<br>
      聯絡地址：高雄市苓雅區憲政路138號<br>
      🤝 請與您的個管員聯繫，將很快協助安排喔！
    `
  },

  '#左營區心理諮商機構': {
    type: 'rich-text',
    content: '左營區心理諮商機構',
    richContent: `
      <b>🏥 左營區心理諮商機構</b><br><br>

      <b>(1) 耕心療癒診所</b><br>
      諮詢地點：耕心療癒診所<br>
      聯絡地址：高雄市左營區曾子路332號<br>
      🤝 請與您的個管員聯繫，將很快協助安排喔！<br><br>

      <b>(2) 欣寧心理治療所</b><br>
      諮詢地點：欣寧心理治療所<br>
      聯絡地址：高雄市左營區重愛路395號<br>
      🤝 請與您的個管員聯繫，將很快協助安排喔！
    `
  },

  '#鳳山區心理諮商機構': {
    type: 'rich-text',
    content: '鳳山區心理諮商機構',
    richContent: `
      <b>🏥 鳳山區心理諮商機構</b><br><br>

      <b>(1) 宇智心理治療所</b><br>
      諮詢地點：宇智心理治療所<br>
      聯絡地址：高雄市鳳山區文衡路490號2F<br>
      🤝 請與您的個管員聯繫，將很快協助安排喔！<br><br>

      <b>(2) 路以心理治療所</b><br>
      諮詢地點：路以心理治療所<br>
      聯絡地址：高雄市鳳山區瑞春街4號1樓<br>
      🤝 請與您的個管員聯繫，將很快協助安排喔！
    `
  },

  '#大寮區心理諮商機構': {
    type: 'rich-text',
    content: '大寮區心理諮商機構',
    richContent: `
      <b>🏥 大寮區心理諮商機構</b><br><br>

      <b>高雄仁愛之家</b><br>
      諮詢地點：高雄仁愛之家<br>
      聯絡地址：高雄市大寮區鳳屏一路509號<br>
      🤝 請與您的個管員聯繫，將很快協助安排喔！
    `
  },

  // ============ C. 指定藥癮戒治及替代治療機構 ============
  '#指定藥癮戒治及替代治療機構': {
    type: 'mixed',
    content: '高雄市指定藥癮戒治及替代治療機構',
    richContent: `
      <b>🏥 高雄市指定藥癮戒治及替代治療機構</b><br><br>

      請勇敢尋求幫助！照顧好自己的身體，是最重要的事情~<br>
      一般疾病或是戒癮療程，透過專業治療和關愛支持，能助您重拾健康生活~💪<br><br>

      <b>詳細機構名單：</b><br><br>

      👉 想了解關於"高雄市指定藥癮戒治機構"詳細資訊請參考：<br>
      <a href="https://orgws.kcg.gov.tw/001/KcgOrgUploadFiles/308/relfile/16830/59614/f13d408c-c1ac-4f19-92d9-60609b01bf32.pdf" target="_blank">點我查看</a><br><br>

      👉 想了解關於"高雄市替代治療執行機構(含美沙冬衛星給藥點)"詳細資訊請參考：<br>
      <a href="https://dsacp.kcg.gov.tw/cp.aspx?n=D467DCCC6379B708" target="_blank">點我查看</a><br><br>

      🤝 <b>請洽詢醫院或您的個管員，將很快協助安排喔！</b>
    `,
    images: [
      {
        url: '/src/assets/gov_images/高雄市藥癮治療機構一覽表.png',
        alt: '高雄市藥癮治療機構一覽表',
        caption: '高雄市藥癮治療機構一覽表'
      }
    ]
  },

  // ============ D. 戒癮資源補助 ============
  '#戒癮資源補助': {
    type: 'cards',
    content: '戒癮雖辛苦~讓我們來當您的後盾！',
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
        description: '生育保健醫療支持補助',
        links: [
          { text: '了解更多', type: 'command', action: '#藥癮個案生育保健醫療支持補助' }
        ]
      },
      {
        id: 'hospitalization-subsidy',
        title: '🏥 戒癮住院治療費用補助',
        description: '減輕您住院的負擔',
        links: [
          { text: '了解更多', type: 'command', action: '#戒癮住院治療費用補助' }
        ]
      },
      {
        id: 'partner-hospitals',
        title: '🏥 住院治療費用補助合作醫院',
        description: '藥癮個案住院治療費用補助合作醫院',
        links: [
          { text: '查看名單', type: 'command', action: '#住院治療費用補助合作醫院' }
        ]
      }
    ]
  },

  '#心理諮商輔導補助': {
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

  '#藥癮個案生育保健醫療支持補助': {
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
        url: '/src/assets/gov_images/前言.png',
        alt: '前言',
        caption: '戒癮治療前言'
      },
      {
        url: '/src/assets/gov_images/高雄市藥癮治療機構一覽表.png',
        alt: '高雄市藥癮治療機構一覽表',
        caption: '高雄市藥癮治療機構一覽表'
      }
    ]
  },

  '#住院治療費用補助合作醫院': {
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
  }
}