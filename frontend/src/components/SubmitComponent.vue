<template>
  <div class="item">
    <div :class="['submit-header', 'status-' + submitEdit.status.toLowerCase()]">
      <div class="line">
        <h4 class="submit-title">ID решения: {{ submitId }}</h4>
        <span class="submit-status">Состояние: <span class="status">{{
            submitEdit.status
          }}</span></span>
      </div>
      <span class="submit-date">{{ submitEdit.updated_at | withoutSeconds }}</span>
    </div>
    <cv-skeleton-text v-if="loading"/>
    <div v-else>
      <code-editor-component v-model="submitEdit.content"/>
      <div class="submit-lang">
        <div>Среда разработки:</div>
        <cv-dropdown
          v-model="submitEdit.de_id"
          :disabled="deOptions.length === 0"
          :items="deOptions"
          class="lang-choice"
          placeholder="Выберите язык программирования">
          <cv-dropdown-item v-for="de in deOptions" :key="de.value" :value="de.value">
            <span>{{ de.name }}</span>
          </cv-dropdown-item>
        </cv-dropdown>
      </div>
    </div>
    <div class="buttons-block-wrapper">
      <div class="handlers bx--row buttons-container">
        <div class="submit-container">
          <div class="input-file-container">
            <input type="file"
                id="file_input" @change="handleFileUpload()">
            <component class="trash-icon icon" :is="TrashCan" @click.prevent.stop="deleteFile"/>
          </div>
          <cv-button
            v-if="!loading"
            :disabled="!canSubmit"
            class="submit-btn"
            v-on:click="confirmSubmit">
            Отправить решение
          </cv-button>

          <cv-button-skeleton v-else></cv-button-skeleton>
          <cv-link
            v-if="!this.cats_account"
            :to="{
            name: 'profile-page',
            params: { userId: userStore.user.id }
          }">
            <cv-tooltip tip="Установите cats аккаунт для отправки"/>
          </cv-link>
        </div>
        <div v-if="isStaff" class="handlers-staff">
          <cv-button
            v-if="!loading"
            :disabled="isAcceptDisabled"
            class="submit-btn accepted"
            v-on:click="acceptSubmit">
            Принять
          </cv-button>
          <cv-button-skeleton v-else></cv-button-skeleton>
          <cv-button
            v-if="!loading"
            :disabled="isRejectDisabled"
            class="submit-btn rejected"
            kind='danger'
            v-on:click="rejectSubmit">
            Отклонить
          </cv-button>
          <cv-button-skeleton v-else></cv-button-skeleton>
        </div>
      </div>
    </div>
      <cv-inline-notification
          v-if="showNotification"
          :kind="notificationKind"
          :sub-title="notificationText"
          class="notification"
          @close="hideNotification"/>
    </div>
</template>

<script lang="ts">
import CodeEditorComponent from '@/components/common/CodeEditorComponent.vue';
import NotificationMixinComponent from '@/components/common/NotificationMixinComponent.vue';
import SubmitModel, { SUBMIT_STATUS } from '@/models/SubmitModel';
import ProblemModel from '@/models/ProblemModel';
import problemStore from '@/store/modules/problem';
import submitStore from '@/store/modules/submit';
import userStore from '@/store/modules/user';
import { AxiosError, AxiosResponse } from 'axios';
import api from '@/store/services/api'
import { de_options } from '@/utils/consts';
import { Component, Prop, Watch } from 'vue-property-decorator';
import _ from 'lodash';
import TrashCan from '@carbon/icons-vue/es/trash-can/20';


@Component({
  components: { CodeEditorComponent },
  filters: {
    withoutSeconds: function (d: string) {
      return new Date(d).toLocaleString([], {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit"
      })
    }
  }
})
export default class SubmitComponent extends NotificationMixinComponent {
  @Prop({ required: true }) submitId!: number;
  @Prop({ required: true }) isStaff!: boolean;
  submit: SubmitModel | null = null;
  submitStore = submitStore;
  problemStore = problemStore;
  userStore = userStore;
  submitEdit: SubmitModel = { ...this.submitStore.defaultSubmit };
  loading = true;
  file_content = '';
  TrashCan = TrashCan;

  get isChanged(): boolean {
    return !_.isEqual(this.submit, this.submitEdit);
  }

  deleteFile(){
    const input = window.document.getElementById('file_input') as HTMLInputElement
    if (input.files?.length) {
      input.value = '';
      this.file_content = '';
    }
  }

  readFileAsync(file: File){
    return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = () => {
      resolve(reader.result);
    };

    reader.onerror = reject;

    reader.readAsText(file);
  })
  }

  async handleFileUpload(){
    const input = window.document.getElementById('file_input') as HTMLInputElement

    if (input.files?.length) {
      this.file_content = await this.readFileAsync(input.files[0]) as string
    }
  }

  get isRejectDisabled() {
    return this.isNewSubmit || this.submit?.status === SUBMIT_STATUS.WRONG_ANSWER;
  }

  get isAcceptDisabled() {
    return this.isNewSubmit || this.submit?.status === SUBMIT_STATUS.OK;
  }

  get canSubmit(): boolean {

    if (this.file_content.length != 0 &&
       this.submitEdit.content?.length !== 0){
      this.notificationKind = 'error';
      this.notificationText = `Отправьте либо текст решения либо файл`;
      this.showNotification = true;
    }
    else {
      this.showNotification = false;
    }

     return (((this.submitEdit.content?.length !== 0
        && this.isChanged) || (this.file_content.length != 0))
        && this.submitEdit.de_id.length !== 0
        && this.cats_account) && !(this.file_content.length != 0 &&
       this.submitEdit.content?.length !== 0);

  }

  get cats_account(): boolean {
    return this.userStore.user.cats_account !== null;
  }

  get problem(): ProblemModel {
    return this.problemStore.currentProblem as ProblemModel;
  }

  // TODO: workflow when already-made submit have de that is disabled
  get deOptions() {
    const options_on = this.problem.de_options.split(',')
    return de_options.filter(option => options_on.includes(option.value));
  }

  get isNewSubmit(): boolean {
    return isNaN(this.submitEdit.id);
  }

  async created() {
    await this.updateSubmit();
  }

  async updateSubmit() {
    this.loading = true;
    if (this.submitId) {
      this.submit = await this.submitStore.fetchSubmitById(this.submitId);
    } else {
      this.submit = null;
    }
    this.submitEdit = (this.submit) ? { ...this.submit }:{ ...this.submitStore.defaultSubmit };
    if (this.submitEdit.de_id === '' && this.deOptions.length === 1)
      this.submitEdit.de_id = this.deOptions[0].value;
    this.loading = false;
  }

  @Watch('submitId')
  onSubmitIdChanged() {
    this.updateSubmit();
  }

  patchSubmit(status: string) {

    this.submitEdit = (this.submit)
        ? { ...this.submit, status: status }
        :{ ...this.submitStore.defaultSubmit };


    api.patch(`/api/submit/${this.submitEdit.id}/`, this.submitEdit)
        .then((response: AxiosResponse<SubmitModel>) => {
          this.submitStore.changeSubmitStatus(response.data);
          this.submit = { ...response.data };
          this.submitEdit = { ...this.submit };
          this.notificationKind = 'success';
          this.notificationText = `Работа оценена: ${status}`;
        })
        .catch((error: AxiosError) => {
          this.notificationKind = 'error';
          this.notificationText = `Что-то пошло не так ${error.message}`
        })
        .finally(() => this.showNotification = true);
  }

  acceptSubmit() {
    this.patchSubmit('OK');
  }

  rejectSubmit() {
    this.patchSubmit('WA');
  }

  confirmSubmit() {

    this.submitEdit = {
      ...this.submitEdit
    }

    if ( this.file_content.length != 0 ){
      this.submitEdit.content = this.file_content
    }

    api.post('/api/submit/', {
      ...this.submitEdit, 'content': this.submitEdit.content,
      'problem': this.problemStore.currentProblem?.id as number,
    }).then((response: AxiosResponse<SubmitModel>) => {
      this.submitStore.addSubmitToArray(response.data);
      this.$emit('submit-created', { id: response.data.id.toString() });
      this.submit = { ...response.data };
      this.submitEdit = { ...this.submit };
      this.problem.last_submit = this.submit;
      this.problemStore.changeCurrentProblem(this.problem)
      this.notificationKind = 'success';
      this.notificationText = 'Попытка отправлена';
    }).catch((error: AxiosError) => {
      this.notificationKind = 'error';
      this.notificationText = `Что-то пошло не так ${error.message}`;
    }).finally(() => this.showNotification = true);
  }

}
</script>

<style lang="stylus" scoped>
.item
  padding 0
  position: relative;

  .notification
    position absolute
    bottom 7rem
    z-index 1

.submit-header
  padding 1em
  border-radius 5px 0 0 0

  .line
    display flex
    justify-content space-between
    padding-bottom 0.5rem

  .submit-status
    font-size 1.5em

  .submit-date
    font-size 1em


.status
  font-weight bold

  &-ok
    color white
    background-color #4EB052

    .submit-data
      color #d6d5d4

  &-aw
    color white
    background-color #8fbd8f

    .submit-data
      color #d6d5d4

  &-wa
    color white
    background-color #DA1E28

    .submit-data
      color #d6d5d4

  &-np
    color white
    background-color #393939

    .submit-data
      color #fafafa


.submit-lang
  display flex
  align-items center
  background var(--cds-ui-03)
  color var(--cds-text-01)
  padding 0.5rem

  div
    height 2.5rem;
    padding 0 0.5rem;
    display flex;
    align-items center;

  .lang-choice
    padding 0

.buttons-block-wrapper
  background-color var(--cds-ui-03)
  border-radius 0 0 0 5px

  .handlers
    display flex
    flex-direction row
    padding 0.5rem
    align-items center
    vertical-align center

.input-file-container
    display flex
    align-items center

  input
    width: 80%


.handlers-staff
  display flex
  width fit-content
  gap 0.5rem

.submit-btn
  width min-content

//justify-content center

.buttons-container
  justify-content space-between
  margin 0 .05rem 0 .5rem

.submit-container
  display flex
  flex-direction row
  align-items center
  gap 0.5rem

</style>


<style lang="stylus" scoped>
.bx--dropdown
  border-bottom 0

/deep/.bx--list-box__field
  display flex

  .bx--list-box__field, ui
    border 0.5px solid #8D8D8D
    background-color var(--cds-ui-background)
    border-radius 10px

.bx--list-box__menu-icon
  top 0.5rem

.cv-button
  padding 0 1rem
</style>
