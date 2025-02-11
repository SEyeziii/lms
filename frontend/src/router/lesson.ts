import problemRoutes from '@/router/problem';
import LessonView from '@/views/LessonView.vue';
import LessonEditView from '@/views/management/LessonEditView.vue';
import LessonProgressView from '@/views/management/LessonProgressView.vue';
import MaterialEditView from '@/views/management/MaterialEditView.vue';
import MaterialView from '@/views/MaterialView.vue';
import ProblemViewLayout from '@/views/ProblemViewLayout.vue';
import { RouteConfig } from 'vue-router';
import examRoutes from "@/router/exam";
import ExamViewLayout from "@/views/ExamViewLayout.vue";

const lessonRoutes: Array<RouteConfig> = [
  {
    path: '',
    name: 'LessonView',
    component: LessonView,
    props: (route) => {
      const lessonId = Number(route.params.lessonId);
      return { ...route.params, lessonId };
    },
  },
  {
    path: 'problem/:problemId',
    component: ProblemViewLayout,
    children: [
      ...problemRoutes,
    ],
    props: (route) => {
      const problemId = Number.parseInt(route.params.problemId as string, 10);
      return { problemId, ...route.params };
    },
  },
  {
    path: 'exam/:examId',
    component: ExamViewLayout,
    children: [
      ...examRoutes,
    ],
    props: (route) => {
      const examId = Number.parseInt(route.params.examId as string, 10);
      return { examId, ...route.params };
    },
  },
  {
    path: 'edit',
    name: 'lesson-edit',
    component: LessonEditView,
    props: (route) => {
      const lessonId = Number.parseInt(route.params.lessonId as string, 10);
      return { lessonId };
    },
  },
  {
    path: 'material/:materialId',
    name: 'MaterialView',
    component: MaterialView,
    props: (route) => {
      const materialId = Number.parseInt(route.params.materialId as string, 10);
      return { materialId, ...route.params };
    },
  },
  {
    path: 'material/:materialId/edit',
    name: 'material-edit',
    component: MaterialEditView,
    props: (route) => {
      const materialId = Number.parseInt(route.params.materialId as string, 10);
      return { materialId };
    },
  },
  {
    path: 'progress',
    name: 'lesson-progress',
    component: LessonProgressView,
    props: (route) => {
      const lessonId = Number.parseInt(route.params.lessonId as string, 10);
      return { lessonId };
    },
  },
];


export default lessonRoutes;
