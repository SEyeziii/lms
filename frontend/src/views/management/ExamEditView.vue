<template>
  <div class="bx--grid">
    <div class="bx--row header">
      <div class="bx--offset-lg-2 main-title">
        <h1>Редактирование теста</h1>
      </div>
    </div>
    <cv-row v-if="!loading" class="main-items" justify="center">
      <cv-column :lg="{'span' : 8, 'offset' : 2}">
        <div class="exam-container">
          <div :class="expanded ? 'expand-container expanded' : 'expand-container'">
            <div @click="expand" class="expand-container-head">
              <p>Настройки теста</p>
              <component class="expand-btn" :is="expanded ? chevronUp : chevronDown"/>
            </div>
            <div class="expand-fields">
              <cv-dropdown v-model="examEdit.test_mode" class="testing-type-dropdown"
                           label="Способ тестирования"
                           placeholder="Выберите способ тестирования">
                <cv-dropdown-item value="auto">Auto</cv-dropdown-item>
                <cv-dropdown-item value="manual">Manual</cv-dropdown-item>
                <cv-dropdown-item value="auto_and_manual">Auto & Manual</cv-dropdown-item>
              </cv-dropdown>
              <cv-text-input v-model.trim="examEdit.name" label="Название теста">
                <template v-if="!examEdit.name.length" slot="invalid-message">
                  {{ emptyFieldText }}
                </template>
              </cv-text-input>
              <cv-text-area v-model="examEdit.description" label="Описание (опционально)"/>
              <!--              <cv-date-picker kind="single" date-label="Дедлайн"/>-->
            </div>
          </div>
          <div class="questions" v-for="(question, index) in examEdit.questions" :key="index">
            <test-question-component
              @set-fields-empty="setFieldsEmpty($event.isEmpty, $event.question)"
              :exam="examEdit" :_question="question" :test-id="examEdit.id"
              :invalid-prop="invalidProp"
              @delete-question="deleteQuestion(question)"/>
          </div>
          <div class="action-container">
            <div class="change-container">
              <div class="change">
                <cv-button v-if="!isExamChanging" @click="changeExam" :disabled="!isChanged">
                  Изменить
                </cv-button>
                <cv-button-skeleton v-else></cv-button-skeleton>
              </div>
              <cv-inline-notification
                v-if="showNotification"
                @close="() => showNotification=false"
                :kind="notificationKind"
                :sub-title="notificationText"/>
            </div>
            <div class="action-btns">
              <component class="action-btn" :is="addAlt" @click="addQuestion"/>
              <!--              <component class="action-btn" :is="image24"/>-->
              <!--              <component class="action-btn" :is="videoAdd"/>-->
              <!--              <component class="action-btn" :is="attachment"/>-->
            </div>
          </div>
        </div>
      </cv-column>
    </cv-row>
    <div v-else class="bx--row">
      <div class="bx--offset-lg-2">
        <cv-loading/>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop } from "vue-property-decorator";
import NotificationMixinComponent from "@/components/common/NotificationMixinComponent.vue";
import TestQuestionComponent from "@/components/ExamQuestionComponent.vue";
import ExamModel from "@/models/ExamModel";
import examStore from "@/store/modules/exam";
import questionStore from "@/store/modules/question";
import chevronUp from "@carbon/icons-vue/lib/chevron--up/24";
import chevronDown from "@carbon/icons-vue/lib/chevron--down/24";
import addAlt from "@carbon/icons-vue/lib/add--alt/24";
import videoAdd from "@carbon/icons-vue/lib/video--add/24";
import image24 from "@carbon/icons-vue/lib/image/24";
import attachment from "@carbon/icons-vue/lib/attachment/24";
import _ from "lodash";
import QuestionModel from "@/models/QuestionModel";
import api from "@/store/services/api";

@Component({
  components: {
    TestQuestionComponent,
    chevronUp,
    chevronDown,
    addAlt,
    videoAdd,
    image24,
    attachment,
  }
})
export default class ExamEditView extends NotificationMixinComponent {
  @Prop({ required: true }) examId!: number;

  examStore = examStore;
  questionStore = questionStore;
  chevronUp = chevronUp;
  chevronDown = chevronDown;
  image24 = image24;
  addAlt = addAlt;
  videoAdd = videoAdd;
  attachment = attachment;
  expanded = false;
  loading = false;
  isExamChanging = false;
  emptyFieldText = '';
  invalidProp = false;
  fieldsValid = new Set<number>();

  exam: ExamModel = { ...examStore.newExam };
  examEdit = { ...this.exam };

  async created() {
    this.loading = true;
    this.emptyFieldText = 'Заполните поле!';
    this.exam = await this.examStore.fetchExamById(this.examId);
    if (!this.exam.questions.length) {
      this.exam.questions.push(
        _.cloneDeep({
          ...this.questionStore.newQuestion,
          index: 0,
        })
      )
    }
    this.examEdit = _.cloneDeep(this.exam);
    this.loading = false;
  }

  get isChanged() {
    return !_.isEqual(this.exam, this.examEdit);
  }

  expand() {
    this.expanded = !this.expanded;
  }

  setFieldsEmpty(isEmpty: boolean, question: number) {
    isEmpty ? this.fieldsValid.add(question) : this.fieldsValid.delete(question);
  }

  addQuestion() {
    const newQuestion = _.cloneDeep({
      ...this.questionStore.newQuestion,
      index: this.exam.questions.length > 0 ? Math.max(...this.exam.questions.map(question => question.index)) + 1 : 0,
    });
    this.examEdit.questions.push(newQuestion);
    this.examEdit.questions.forEach(value => {
      if (!value.text.length)
        this.fieldsValid.add(value.index);
    })
  }

  deleteQuestion(question: QuestionModel) {
    if (this.examEdit.questions.length > 1) {
      this.examEdit.questions = this.examEdit.questions.filter(x => x !== question);
    }
  }

  async changeExam() {
    this.isExamChanging = true;
    if (this.fieldsValid.size || !this.examEdit.name.length) {
      this.notificationText = 'Проверьте правильность введенных данных';
      this.notificationKind = 'error';
      this.showNotification = true;
      this.isExamChanging = false;
      this.invalidProp = true;
      return;
    }
    this.examEdit.max_points = 0;
    this.examEdit.questions.forEach((question) => {
      this.examEdit.max_points += question.points;
    })
    await api.patch(`/api/exam/${this.examId}/`, {
      ...this.examEdit,
      questions: this.examEdit.questions
    }).then(response => {
      this.notificationKind = 'success';
      this.notificationText = 'Тест успешно изменен';
      this.exam = response.data;
      this.examStore.changeCurrentExam(this.exam);
    }).catch(error => {
      this.examEdit.max_points = this.exam.max_points;
      this.notificationText = `Что-то пошло не так: ${error.message}`;
      this.notificationKind = 'error';
    }).finally(() => {
      this.showNotification = true;
      this.isExamChanging = false;
    })
  }
}
</script>

<style scoped lang="stylus">
.main-items
  color var(--cds-text-01)

.exam-container
  min-width 45rem

.expand-container-head
  cursor pointer
  display flex
  align-items center
  justify-content space-between
  margin-bottom 1rem

.expand-container
  max-height 3.25rem
  overflow hidden
  transition all .3s ease
  background var(--cds-ui-01)
  padding 1rem

.expand-container.expanded
  max-height 500px

.testing-type-dropdown
  width 40%

span
  margin-bottom 0.25rem

/deep/ .bx
  &--text
    &-input
      background-color var(--cds-ui-background)

    &-area
      background-color var(--cds-ui-background)

  &--list
    &-box
      background-color var(--cds-ui-background)

      &__field
        display flex

  &--number
    input[type=number]
      background-color var(--cds-ui-background)

/deep/ .bx--date-picker__input
  background-color var(--cds-ui-background)
  width auto

.action-container
  display flex
  justify-content space-between

.expand-fields
  display flex
  flex-direction column
  gap 1rem

.action-btns
  background var(--cds-ui-01)
  display flex
  gap 1rem
  border-radius 5px
  margin-top 0.5rem
  align-self flex-start
  padding 1rem

.action-btn
  cursor pointer
  transition ease-in-out 0.1s

.action-btn:active
  transform scale(0.9)

.change-container
  display flex
  gap 1rem
  flex-direction row
  width 60%

.change
  background-color var(--cds-ui-01)
  border-radius 5px
  padding 1rem
  width fit-content
  margin-top 0.5rem
</style>
