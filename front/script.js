document.addEventListener('DOMContentLoaded', function () {
  const gradeInputs = document.getElementById('grade-inputs');
  const addButton = document.getElementById('add-grade');
  const submitButton = document.getElementById('submit');
  const resultDiv = document.getElementById('result');
  const evaluationDiv = document.getElementById('evaluation');

  addGradePair();

  addButton.addEventListener('click', addGradePair);

  submitButton.addEventListener('click', async function () {
    const userInfo = {
      name: document.getElementById('name').value.trim(),
      gender: document.querySelector('input[name="gender"]:checked').value,
      age: document.getElementById('age').value,
      grade: document.getElementById('grade').value
    };

    if (!userInfo.name || !userInfo.age || !userInfo.grade) {
      alert('请填写完整的个人信息');
      return;
    }

    const grades = collectGrades();
    if (!grades) return;

    showLoading();

    try {
      const response = await getEvaluation(userInfo, grades);
      showEvaluation(response);
    } catch (error) {
      console.error('获取评价失败:', error);
      evaluationDiv.innerHTML = `<p class="error">获取评价失败: ${error.message}</p>`;
      resultDiv.classList.remove('hidden');
      hideLoading();
    }
  });

  function addGradePair() {
    const pairDiv = document.createElement('div');
    pairDiv.className = 'grade-pair';

    const subjectInput = document.createElement('input');
    subjectInput.type = 'text';
    subjectInput.placeholder = '科目名称';
    subjectInput.required = true;

    const gradeInput = document.createElement('input');
    gradeInput.type = 'number';
    gradeInput.min = '0';
    gradeInput.max = '100';
    gradeInput.placeholder = '成绩 (0-100)';
    gradeInput.required = true;

    const deleteButton = document.createElement('button');
    deleteButton.textContent = '删除';
    deleteButton.addEventListener('click', function () {
      gradeInputs.removeChild(pairDiv);
    });

    pairDiv.appendChild(subjectInput);
    pairDiv.appendChild(gradeInput);
    pairDiv.appendChild(deleteButton);
    gradeInputs.appendChild(pairDiv);
  }

  function collectGrades() {
    const pairs = document.querySelectorAll('.grade-pair');
    const grades = {};
    let hasError = false;

    pairs.forEach((pair, index) => {
      const subjectInput = pair.querySelector('input[type="text"]');
      const gradeInput = pair.querySelector('input[type="number"]');

      const subject = subjectInput.value.trim();
      const gradeStr = gradeInput.value.trim();
      const grade = gradeStr ? parseInt(gradeStr) : NaN;

      if (!subject) {
        alert(`请填写第${index + 1}个科目的名称`);
        subjectInput.focus();
        hasError = true;
        return;
      }

      if (isNaN(grade) || grade < 0 || grade > 100) {
        alert(`请为${subject}输入有效的成绩(0-100)`);
        gradeInput.focus();
        hasError = true;
        return;
      }

      grades[subject] = grade;
    });

    return hasError ? null : grades;
  }

  async function getEvaluation(userInfo, grades) {
    const requestData = {
      name: userInfo.name,
      gender: userInfo.gender,
      age: parseInt(userInfo.age),
      grade: userInfo.grade,
      grades: grades
    };

    const [evaluateRes, suggestRes] = await Promise.all([
      fetch('http://localhost:8080/get_evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
      }),
      fetch('http://localhost:8080/get_suggest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
      })
    ]);

    if (!evaluateRes.ok || !suggestRes.ok) {
      throw new Error('API请求失败');
    }

    const evaluation = await evaluateRes.json();
    const advice = await suggestRes.json();

    return {
      evaluation: evaluation.result || evaluation,
      advice: advice.result || advice
    };
  }

  function showLoading() {
    submitButton.disabled = true;
    submitButton.innerHTML = '<div class="spinner"></div> 处理中...';
  }

  function hideLoading() {
    submitButton.disabled = false;
    submitButton.textContent = '获取评价建议';
  }

  function markdownToHtml(text) {
    if (!text) return '';
    const compactText = text.replace('\n', '\n\n');
    return marked.parse(compactText);
  }

  // ✅ 改进后的 showEvaluation 函数
  async function showEvaluation(result) {
    resultDiv.classList.remove('hidden');
    evaluationDiv.innerHTML = '';
    document.getElementById('advice').innerHTML = '';
    hideLoading();

    const evaluationText = typeof result.evaluation === 'object'
      ? result.evaluation.result || JSON.stringify(result.evaluation, null, 2)
      : result.evaluation || '暂无评价结果';

    const adviceText = typeof result.advice === 'object'
      ? result.advice.result || JSON.stringify(result.advice, null, 2)
      : result.advice || '暂无学习建议';

    evaluationDiv.innerHTML = markdownToHtml(evaluationText);
    document.getElementById('advice').innerHTML = markdownToHtml(adviceText);
    
    // 添加结果提示弹窗
    alert('评价结果已生成，请查看下方内容');
  }
});
