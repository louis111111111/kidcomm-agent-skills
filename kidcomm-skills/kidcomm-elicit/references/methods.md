# 学术验证方法速查（kidcomm-elicit 的方法底座）

> 本 Skill 的引导方式不是拍脑袋，而是对应已被研究验证的儿童访谈/表达方法。写 prompt 与脚本时对照使用。

## 1. 讲故事 / 故事续写（Story Stems）
- **来源**：Narrative and play-based interviewing（哥本哈根大学）；COVID 玩乐研究中的 Story Completion  vignette。
- **做法**：给一个开头故事（常带玩偶/图），让孩子"接着说发生什么"。降低表达门槛，让孩子用自己话讲。
- **本 Skill 用法**：modality=`story_stem`，生成一段适龄开头 + 引导续写的问题。

## 2. 角色扮演 / 动作情境（Role-play / Show & Tell）
- **来源**：Narrative & play-based interviewing 的 child-centred play；LSE「采访儿童」工具包的 puppets/dolls；Show & Tell。
- **做法**：用玩偶/情境让孩子"演出来"，比直接问答更自然。
- **本 Skill 用法**：modality=`roleplay`，生成一段亲子可在家演的短情境脚本（无物理动作，靠语音+画面引导）。

## 3. 分步引导提问（Guided Questions：暖场→开放→聚焦→细节）
- **来源**：LSE 工具包（先暖场简单问题、避免诱导性提问、结尾让孩子纠错）；临床儿童访谈连续体（open-ended → focused → detail）。
- **做法**：先用轻松问题暖场，再开放提问，逐步聚焦到细节；**绝不暗示标准答案**。
- **本 Skill 用法**：modality=`guided_questions`，生成 question_sequence，严格按暖场→开放→聚焦→细节排序，且每句非诱导。

## 4. 画图 / 画写（Drawing / Draw & Write）
- **来源**：LSE 工具包、AIFS 儿童参与评估、COVID 研究的 Draw & Write。
- **做法**：让孩子画出来再讲，画图是记忆线索与表达替代通道。
- **本 Skill 用法**：modality=`drawing`，生成 drawing_prompt + 后续"讲讲你画了什么"的引导。

## 5. 成员核查（Member-check）
- **来源**：LSE 工具包明确"结尾把理解反馈给孩子，问对不对/要不要改"；In My Shoes 用图标确认。
- **做法**：把推导的意思抛回给孩子确认，防误读。
- **本 Skill 用法**：summarize 必带 `member_check_question`，交回孩子确认；孩子纠正则重推。

## 6. 低压力 / 权力平衡
- **来源**：In My Shoes「并排坐」降低威胁感；AIFS 让孩子选何时/如何参与。
- **做法**：减少成人-儿童权力差，让孩子更自发。
- **本 Skill 用法**：delivery_notes 强调语气平等、可随时停。

## 对照竞品（写 related work 用）
- **Puppet Interview**：基于 Berkeley Puppet Interview（100+ 论文），固定问卷+玩偶，云端合规但仍上传。
- **AskKids（Save the Children）**：语音/图片答题，给不识字孩子。
- **ChaCha / ARCH / AMA**：LLM 引导儿童分享情绪/事件，但多限定情绪或话题，非通用调研。
- **本 Skill 差异**：通用任意话题 + 自适应非诱导追问 + 本地离线隐私 + Agent Skill 可移植。
