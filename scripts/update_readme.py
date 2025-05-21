import os
from github import Github
import re

# GitHub 토큰 세팅 (Actions 내장 환경 변수로 설정)
gh = Github(os.getenv("GITHUB_TOKEN"))
repo = gh.get_repo(os.getenv("GITHUB_REPOSITORY"))

# 1) 모든 이슈 불러오기
issues = repo.get_issues(state="all")

# 2) 레이블별 카운트 집계
label_counts = {}
total = 0
for issue in issues:
    # 'review' 라벨이 붙은 이슈만 대상으로 할 수도 있음
    if "review" not in [l.name for l in issue.labels]:
        continue
    total += 1
    for lbl in issue.labels:
        label_counts[lbl.name] = label_counts.get(lbl.name, 0) + 1

# 3) 비율 텍스트 생성
stats_md = "No reviews yet."
if total > 0:
    stats_md = "\n".join(
        f"- **{lbl}**: {count}건 ({count/total*100:.1f}%)"
        for lbl, count in sorted(label_counts.items(), key=lambda x:-x[1])
    )

# 4) 제목 리스트 생성
titles_md = "\n".join(f"- {issue.title}" 
                      for issue in issues 
                      if "review" in [l.name for l in issue.labels])

# 5) README 갱신
readme = repo.get_contents("README.md")
content = readme.decoded_content.decode()
content = re.sub(
    r"<!-- stats-start -->.*?<!-- stats-end -->",
    f"<!-- stats-start -->\n{stats_md}\n<!-- stats-end -->",
    content, flags=re.S
)
content = re.sub(
    r"<!-- list-start -->.*?<!-- list-end -->",
    f"<!-- list-start -->\n{titles_md}\n<!-- list-end -->",
    content, flags=re.S
)
repo.update_file("README.md", "chore: update stats & list", content,
                 readme.sha)
