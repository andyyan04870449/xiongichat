// 婦幼專區的詳細資料
import { CommandResponse } from '../types/message'

export const MATERNAL_CHILD_RESOURCES: Record<string, CommandResponse> = {
  // ============ 主選單 ============
  '#婦幼專區': {
    type: 'cards',
    content: '今天想要了解什麼資訊呢？',
    cards: [
      {
        id: 'maternal-care',
        title: '👶 母嬰照護',
        description: '陪你同行，孕釀希望！從孕前準備到產後照護，每個階段都值得仔細呵護。',
        links: [
          { text: '查看詳情', type: 'command', action: '#母嬰照護' }
        ]
      },
      {
        id: 'reproductive-health',
        title: '🏥 生育保健',
        description: '藥癮個案生育保健醫療支持補助',
        links: [
          { text: '查看詳情', type: 'command', action: '#生育保健' }
        ]
      },
      {
        id: 'maternal-subsidy',
        title: '💰 婦幼醫療補助',
        description: '了解婦幼醫療補助，點擊查看詳情。',
        links: [
          { text: '查看詳情', type: 'command', action: '#婦幼醫療補助' }
        ]
      },
      {
        id: 'counseling-program',
        title: '👩 輔導方案',
        description: '女性藥癮個案支持團體會是您最堅強的後盾！',
        links: [
          { text: '查看詳情', type: 'command', action: '#輔導方案' }
        ]
      },
      {
        id: 'menstrual-equity',
        title: '🌸 月經平權',
        description: '月經平權政策與生育保健知能服務',
        links: [
          { text: '查看詳情', type: 'command', action: '#月經平權' }
        ]
      }
    ]
  },

  // ============ A. 母嬰照護 ============
  '#母嬰照護': {
    type: 'cards',
    content: '陪你同行，孕釀希望！從孕前準備到產後照護，每個階段都值得仔細呵護。讓我們一起迎接新生命的到來！政府有提供很多資源可以幫助媽媽與寶寶們唷！可以聯繫相關單位尋求資源協助~',
    cards: [
      {
        id: 'care-guide',
        title: '📖 母嬰照護指引',
        description: '陪你同行，孕釀希望❤️',
        links: [
          { text: '查看指引', type: 'command', action: '#母嬰照護指引' }
        ]
      },
      {
        id: 'welfare-center',
        title: '🏢 社會福利中心據點',
        description: '18處社會福利服務中心提供便捷服務',
        links: [
          { text: '了解更多', type: 'command', action: '#社會福利中心據點' }
        ]
      },
      {
        id: 'parent-child-center',
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

  '#母嬰照護指引': {
    type: 'mixed',
    content: '母嬰照護',
    richContent: `
      <b>👶 母嬰照護</b><br><br>

      陪你同行，孕釀希望❤️<br><br>

      從孕前準備到產後照護，每個階段都有重要的注意事項。<br>
      讓我們一起守護母嬰健康，迎接新生命的到來！
    `,
    images: [
      {
        url: '/src/assets/gov_images/陪妳同行.png',
        alt: '陪妳同行',
        caption: '陪妳同行，一起迎接新生命'
      },
      {
        url: '/src/assets/gov_images/孕前到產後每階段要注意的事.png',
        alt: '孕前到產後每階段要注意的事',
        caption: '孕期各階段重要提醒'
      },
      {
        url: '/src/assets/gov_images/女生藥物濫用原因.png',
        alt: '女生藥物濫用原因',
        caption: '了解藥物濫用的原因'
      },
      {
        url: '/src/assets/gov_images/藥物濫用對孕婦及胎兒影響.png',
        alt: '藥物濫用對孕婦及胎兒影響',
        caption: '保護母嬰健康'
      }
    ]
  },

  '#社會福利中心據點': {
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

  // ============ B. 生育保健 ============
  '#生育保健': {
    type: 'mixed',
    content: '藥癮個案生育保健醫療支持補助',
    richContent: `
      <b>🏥 藥癮個案生育保健醫療支持補助</b><br><br>

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

  // ============ C. 婦幼醫療補助 ============
  '#婦幼醫療補助': {
    type: 'cards',
    content: '了解婦幼醫療補助，點擊查看詳情。',
    cards: [
      {
        id: 'reproductive-subsidy',
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

  // ============ D. 輔導方案 ============
  '#輔導方案': {
    type: 'cards',
    content: '女性藥癮個案支持團體會是您最堅強的後盾！',
    cards: [
      {
        id: 'program-content',
        title: '💪 了解方案內容',
        description: '女性藥癮個案支持團體',
        links: [
          { text: '查看詳情', type: 'command', action: '#了解方案內容' }
        ]
      }
    ]
  },

  '#了解方案內容': {
    type: 'rich-text',
    content: '女性藥癮個案支持團體',
    richContent: `
      <b>👩 女性藥癮個案支持團體</b><br><br>

      主要為幫助女性藥癮個案重拾健康、快樂的生活。<br><br>

      透過團體的力量、定期性的活動，改善女性藥癮個案經濟、情感、人際關係、生育及家庭等5面向常見問題，促進身心健康安全~❤️<br><br>

      🤝 <b>請與您的個管員聯繫，將很快協助安排喔！</b>
    `
  },

  // ============ E. 月經平權 ============
  '#月經平權': {
    type: 'mixed',
    content: '月經平權',
    richContent: `
      <b>🌸 月經平權</b><br><br>

      月經平權是指消除在保健方面對婦女的歧視，在性別平等的基礎上取得各種包括有關計劃生育的保健服務。❤️<br><br>

      毒防局推動月經平權暨提升藥癮個案生育保健知能，如符合設籍或實際居住高雄市列管中之15-49歲育齡婦女藥癮個案，個管員將進行家庭訪視，提供月事所需相關物品，並依個案需求，提供個別用藥、生育保健相關討論。<br><br>

      <b>服務對象：</b><br>
      符合設籍或實際居住高雄市列管中之15-49歲育齡婦女藥癮個案<br><br>

      <b>服務方式：</b><br>
      • 個管員進行家庭訪視<br>
      • 提供月事所需相關物品<br>
      • 依個案需求，提供個別用藥、生育保健相關討論
    `,
    images: [
      {
        url: '/src/assets/gov_images/月事安心_事事順心.jpg',
        alt: '月事安心_事事順心',
        caption: '月事安心，事事順心'
      },
      {
        url: '/src/assets/gov_images/避孕的重要性.jpg',
        alt: '避孕的重要性',
        caption: '了解避孕的重要性'
      }
    ]
  }
}