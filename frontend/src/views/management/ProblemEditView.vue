<template>
  <div class="bx--grid">
    <div class="bx--row header"><h1>Редактирование задачи</h1></div>
    <div v-if="showNotification" class="bx--row">
      <cv-inline-notification
        :kind="notificationKind"
        :sub-title="notificationText"
        @close="() => showNotification = false"
      />
    </div>
    <div class="bx--row">
      <div class="bx--col-lg-7 items">
        <cv-skeleton-text
          v-if="loading"
          :line-count="6"
          :paragraph="true"
          :width="'80%'"/>
        <div v-else>
          <cv-text-input v-model.trim="problemEdit.name" label="Название"/>
          <cv-text-area v-model.trim="problemEdit.description" label="Описание"/>
          <div>
            <br>
            <cv-multi-select
              v-model="deChecks"
              :options="deOptions"
              class="course--de"
              label="Выберите среды разработки"
              title="Доступные среды для отправки решений"
              @change="deChanged">
              <template slot="helper-text">
                <cv-tooltip tip="При пустом списке будет использованы настройки курса"/>
              </template>
            </cv-multi-select>
          </div>
        </div>
        <span style="padding-top: 20px">Выберите способ тестирования</span>
            <cv-radio-group style="margin-top: 10px; padding-bottom: 20px">

              <cv-radio-button @change = modChanged
                               name="group-1"
                               label="автоматическое"
                               value="auto"
                               v-model="testingMode"
              />
              <cv-radio-button @change = modChanged
                               name="group-1"
                               label="ручное"
                               value="manual"
                               v-model="testingMode"
              />
              <cv-radio-button @change = modChanged
                               name="group-1"
                               label="автоматическое и ручное"
                               value="auto_and_manual"
                               v-model="testingMode"
              />

            </cv-radio-group>
        <cv-button-skeleton v-if="problemUpdating"/>
        <cv-button
          v-else :disabled="!isChanged || loading"
          class="finishButton"
          v-on:click="updateProblem">
          Обновить задачу
        </cv-button>

      </div>
      <div class="bx--col-lg-1"></div>
      <div class="bx--col-lg-7 items">
        <h4>cats версия задачи</h4>
        <cv-skeleton-text
          v-if="catsProblemLoading || catsProblem"
          :line-count="6"
          :paragraph="true"
          :width="'80%'"/>
        <CatsProblemComponent v-else :catsProblem="catsProblem"/>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import CatsProblemComponent from '@/components/EditProblem/CatsProblemComponent.vue';
import Problem from '@/components/lists/ProblemListComponent.vue';
import CatsProblemModel from '@/models/CatsProblemModel';
import ProblemModel from '@/models/ProblemModel';
import problemStore from "@/store/modules/problem";
import _ from 'lodash';
import { Component, Prop, Vue } from 'vue-property-decorator';

@Component({ components: { Problem, CatsProblemComponent } })
export default class ProblemEditView extends Vue {
  private store = problemStore;
  @Prop() problemId!: number;
  problem = { ...this.store.getNewProblem };
  problemEdit = { ...this.store.getNewProblem };
  loading = true;
  catsProblemLoading = true;
  catsProblem: CatsProblemModel | null = null;
  notificationKind = 'success';
  notificationText = '';
  showNotification = false;
  problemUpdating = false;
  testingMode = '';
  deChecks: string[] = [];
  deOptions =  [
  {
    value: '3', label: 'Cross-platform C/C++ compiler',
    name: 'Cross-platform C/C++ compiler', disabled: false,
  },
  {
    value: '681949', label: 'Python 3.8.1',
    name: 'Python 3.8.1', disabled: false,
  },
];


  deChanged() {
    this.problemEdit = { ...this.problemEdit, de_options: this.deChecks.sort().join(',') };
  }
  modChanged(){
    this.problemEdit = { ...this.problemEdit, test_mode: this.testingMode }
  }

  get isChanged(): boolean {
    return !_.isEqual(this.problem, this.problemEdit);
  }

  async created() {
    this.loading = true;
    this.problem = await this.store.fetchProblemById(this.problemId);
    this.problemEdit = { ...this.problem };
    this.deChecks = this.problemEdit.de_options.split(',');
    this.loading = false;
    this.catsProblem = await this.store.fetchCatsProblemById(this.problem.cats_id)
    this.testingMode = this.problemEdit.test_mode;
    this.catsProblemLoading = false;
  }

  updateProblem(): void {
    this.problemUpdating = true;
    const request = this.store.patchProblem(this.problemEdit);
    request.then(response => {
      this.notificationKind = 'success';
      this.notificationText = 'Задача успешно обновлена'
      this.problem = response.data;
      this.problemEdit = { ...this.problem };
    });
    request.catch(error => {
      this.notificationText = `Что-то пошло не так: ${error.message}`;
      this.notificationKind = 'error';
    })
    request.finally(() => {
      this.showNotification = true;
      this.problemUpdating = false;
    });

  }
}
</script>

<style scoped lang="stylus">
.items
  background-color var(--cds-ui-02)

.header
  padding-bottom 1.5rem
  padding-top 1rem

</style>
