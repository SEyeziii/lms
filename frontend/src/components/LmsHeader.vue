<template>
  <cv-header class="lms-header" aria-label="Carbon tutorial">
    <cv-skip-to-content href="#main-content"> Skip to content</cv-skip-to-content>
    <cv-header-menu-button v-if="courseSelected" aria-controls="side-nav" aria-label="Header menu"/>
    <cv-header-name prefix="dvfu" to="/"><span class="lms">lms</span></cv-header-name>
    <cv-header-nav v-if="courseSelected">
      <cv-header-menu-item
        :to="{
          name: 'course-solutions-list',
          params: { courseId: this.$route.params.courseId }
        }"
      >
        Решения
      </cv-header-menu-item>
    </cv-header-nav>
    <cv-header-nav v-if="isStaff && courseSelected">
      <cv-header-menu-item
        :to="{
          name: 'course-progress',
          params: { courseId: this.$route.params.courseId }
        }"
      >
        Успеваемость
      </cv-header-menu-item>
    </cv-header-nav>
    <cv-header-nav v-if="isStaff && lessonSelected">
      <cv-header-menu-item
        :to="{
          name: 'lesson-progress',
          params: { lessonId: this.$route.params.lessonId }
        }"
      >
        Успеваемость урока
      </cv-header-menu-item>
    </cv-header-nav>
    <cv-header-nav v-if="isStaff && courseSelected">
      <cv-header-menu-item
        :to="{ name: 'course-calendar', params: { courseId: this.$route.params.courseId } }"
      >
        Календарь
      </cv-header-menu-item>
    </cv-header-nav>
    <cv-header-nav v-if="isStaff && courseSelected && !lessonSelected && !problemSelected">
      <cv-header-menu-item
        :to="{ name: 'course-edit', params: { courseId: this.$route.params.courseId } }"
      >
        Редактировать курс
      </cv-header-menu-item>
    </cv-header-nav>
    <cv-header-nav
      v-if="isStaff && lessonSelected && !problemSelected && !materialSelected && !examSelected">
      <cv-header-menu-item
        :to="{ name: 'lesson-edit', params: { lessonId: this.$route.params.lessonId } }"
      >
        Редактировать урок
      </cv-header-menu-item>
    </cv-header-nav>
    <cv-header-nav v-if="isStaff && problemSelected">
      <cv-header-menu-item
        :to="{ name: 'problem-edit', params: { problemId: this.$route.params.problemId } }"
      >
        Редактировать задачу
      </cv-header-menu-item>
    </cv-header-nav>
    <cv-header-nav v-if="isStaff && examSelected">
      <cv-header-menu-item
        :to="{ name: 'exam-edit', params: { examId: this.$route.params.examId } }"
      >
        Редактировать тест
      </cv-header-menu-item>
    </cv-header-nav>
    <cv-header-nav v-if="isStaff && materialSelected">
      <cv-header-menu-item
        :to="{ name: 'material-edit', params: { materialId: this.$route.params.materialId } }"
      >
        Редактировать материалы
      </cv-header-menu-item>
    </cv-header-nav>

    <template slot="left-panels">
      <cv-side-nav id="side-nav" fixed>
        <cv-side-nav-items>
          <cv-header-side-nav-items>
            <cv-header-menu-item
              v-if="courseSelected"
              :to=" { name: 'course-solutions-list', params: { courseId: this.$route.params.courseId } }"
            >
              Решения
            </cv-header-menu-item>
            <cv-header-menu-item
              v-if="isStaff && courseSelected"
              :to="{ name: 'course-progress', params: { courseId: this.$route.params.courseId } }"
            >
              Успеваемость
            </cv-header-menu-item>
            <cv-header-menu-item
              v-if="lessonSelected"
              :to="{ name: 'lesson-progress', params: { lessonId: this.$route.params.lessonId } }"
            >
              Успеваемость урока
            </cv-header-menu-item>
            <cv-header-menu-item
              v-if="isStaff && courseSelected"
              :to="{ name: 'course-calendar', params: { courseId: this.$route.params.courseId } }"
            >
              Календарь
            </cv-header-menu-item>
            <cv-header-menu-item
              v-if="isStaff && courseSelected && !lessonSelected && !problemSelected"
              :to="{ name: 'course-edit', params: { courseId: this.$route.params.courseId } }"
            >
              Редактировать курс
            </cv-header-menu-item>
            <cv-header-menu-item
              v-if="isStaff && lessonSelected && !problemSelected && !materialSelected && !examSelected"
              :to="{ name: 'lesson-edit', params: { lessonId: this.$route.params.lessonId } }"
            >
              Редактировать урок
            </cv-header-menu-item>
            <cv-header-menu-item
              v-if="isStaff && problemSelected"
              :to="{ name: 'problem-edit', params: { problemId: this.$route.params.problemId } }"
            >
              Редактировать задачу
            </cv-header-menu-item>
            <cv-header-menu-item
              :to="{ name: 'exam-edit', params: { examId: this.$route.params.examId } }"
            >
              Редактировать тест
            </cv-header-menu-item>
            <cv-header-menu-item
              v-if="isStaff && materialSelected"
              :to="{ name: 'material-edit', params: { materialId: this.$route.params.materialId } }"
            >
              Редактировать материалы
            </cv-header-menu-item>
          </cv-header-side-nav-items>
        </cv-side-nav-items>
      </cv-side-nav>
    </template>
    <template slot="header-global">
      <cv-header-global-action aria-label="Notifications"
                               aria-controls="notifications">
        <notification-20/>
      </cv-header-global-action>
      <cv-header-global-action aria-label="User avatar"
                               aria-controls="account">
        <user-avatar-20/>
      </cv-header-global-action>
    </template>

    <template slot="right-panels">
      <cv-header-panel class="" id="account">
        <UserView :userProp="userStore.user" class="user-view"/>
        <cv-switcher>
          <template>
            <cv-switcher-item>
              <cv-switcher-item-link
                :to="{
                  name: 'profile-page',
                  params:  { userId: userStore.user.id }
                }"
              >
                Профиль
              </cv-switcher-item-link>
            </cv-switcher-item>
            <cv-switcher-item>
              <cv-switcher-item-link to="/">
                Мои курсы
              </cv-switcher-item-link>
            </cv-switcher-item>
            <cv-switcher-item>
              <cv-switcher-item-link :to="{
                  name: 'course-add',
                  params:  { courseId: null }
                }"
              >
                Создать курс
              </cv-switcher-item-link>
            </cv-switcher-item>
            <cv-switcher-item>
              <cv-switcher-item-link @click="logout"> Выйти</cv-switcher-item-link>
            </cv-switcher-item>
          </template>
        </cv-switcher>
        <cv-toggle class="toggle-theme" label="Тема" value="" v-model="current_theme">
          <template slot="text-left">
            <component :is="iconLight"></component>
          </template>
          <template slot="text-right">
            <component :is="iconDark"></component>
          </template>
        </cv-toggle>
      </cv-header-panel>
    </template>

    <template slot="right-panels">
      <cv-header-panel class="" id="notifications">
        <span class="acc_text">Оповещения</span>
        <cv-switcher>
          <template>
            <cv-switcher-item>
              <cv-switcher-item-link to="/">
                <cv-toast-notification
                  caption="текст оповещения"
                  kind="info"
                  title="тестовое уведомление"/>
              </cv-switcher-item-link>
            </cv-switcher-item>
          </template>
        </cv-switcher>
      </cv-header-panel>
    </template>
  </cv-header>
</template>

<script lang="ts">
import UserView from "@/components/UserComponent.vue";
// import LoginAsUserModal from "@/components/LoginAsUserModal.vue";
import userStore from "@/store/modules/user";
import AppSwitcher20 from '@carbon/icons-vue/es/app-switcher/20';
import Notification20 from '@carbon/icons-vue/es/notification/20';
import UserAvatar20 from '@carbon/icons-vue/es/user--avatar/20';
import Light20 from '@carbon/icons-vue/es/light/20'
import Asleep20 from '@carbon/icons-vue/es/asleep/20'
import Vue from 'vue';
import Component from 'vue-class-component';
import tokenStore from '@/store/modules/token'
import { THEMES } from '@/utils/consts'
import { Watch } from "vue-property-decorator";

@Component({
  components: {
    UserView,
    // LoginAsUserModal,
    Notification20,
    UserAvatar20,
    AppSwitcher20,
    Asleep20,
    Light20
  }
})
export default class LmsHeader extends Vue {
  @Watch('current_theme')
  changeTheme() {
    this.$emit("toggle-theme", this.current_theme ? THEMES.g90 : THEMES.g10);
  }

  iconLight = Light20;
  iconDark = Asleep20;

  current_theme = this.getTheme;
  themes = THEMES;
  userStore = userStore;

  async logout() {
    await tokenStore.logout();
    window.location.reload();
  }

  get courseSelected(): boolean {
    return this.$route.params.hasOwnProperty('courseId') && this.$route.params['courseId'] != null;
  }

  get lessonSelected(): boolean {
    return this.$route.params.hasOwnProperty('lessonId') && this.$route.params['lessonId'] != null;
  }

  get problemSelected(): boolean {
    return this.$route.params.hasOwnProperty('problemId') && this.$route.params['problemId'] != null;
  }

  get examSelected(): boolean {
    return this.$route.params.hasOwnProperty('examId') && this.$route.params['examId'] != null;
  }

  get materialSelected(): boolean {
    return this.$route.params.hasOwnProperty('materialId') && this.$route.params['materialId'] != null;
  }

  get getTheme(): boolean {
    return localStorage.getItem('theme') === THEMES.g90
  }

  get isStaff(): boolean {
    return this.userStore.user.staff_for.includes(Number(this.$route.params.courseId));
  }
}
</script>

<style scoped lang="stylus">

.lms
  padding-left 5px

.acc_text
  margin: 32px 1rem 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid #525252;

.user-view
  padding-left 30px;
  padding-top 10px;

.toggle-theme
  position absolute
  bottom 0
  margin 0.5rem
</style>
