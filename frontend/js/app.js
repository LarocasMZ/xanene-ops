// XANENE OPS - Frontend Application

class XaneneOps {
    constructor() {
        this.apiBase = '/api';
        this.token = 'test-token';
        this.currentUser = {
            id: 1,
            email: 'admin@xanene.com',
            full_name: 'Admin User',
            role: 'admin',
            is_active: true
        };
        this.currentView = 'kanban';
        this.currentDate = new Date();
        this.users = [];

        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.updateCurrentDate();
        this.showApp();
    }

    setupDragAndDrop() {
        console.log('Setting up drag and drop...');
        // Set up drop zones once on column containers
        const dropZones = {
            'kanban-pending': 'pending',
            'kanban-in_progress': 'in_progress',
            'kanban-completed': 'completed'
        };

        Object.entries(dropZones).forEach(([zoneId, status]) => {
            const zone = document.getElementById(zoneId);
            console.log('Setting up zone:', zoneId, zone ? 'found' : 'NOT FOUND');
            if (!zone) return;

            zone.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                zone.classList.add('bg-blue-50');
                console.log('Drag over:', zoneId);
            });

            zone.addEventListener('dragleave', () => {
                zone.classList.remove('bg-blue-50');
            });

            zone.addEventListener('drop', (e) => {
                e.preventDefault();
                zone.classList.remove('bg-blue-50');
                const taskId = parseInt(e.dataTransfer.getData('text/plain'));
                console.log('Dropped task', taskId, 'on', zoneId, 'new status:', status);
                this.updateTaskStatus(taskId, status);
            });
        });
    }

    async updateTaskStatus(taskId, newStatus) {
        console.log('Updating task', taskId, 'to status', newStatus);
        try {
            await this.api(`/tasks/${taskId}`, {
                method: 'PUT',
                body: JSON.stringify({ status: newStatus })
            });
            console.log('Task updated successfully');
            this.loadTasks();
        } catch (error) {
            console.error('Error updating task:', error);
            alert('Error updating task status: ' + error.message);
        }
    }

    setupEventListeners() {
        // Logout
        document.getElementById('logout-btn')?.addEventListener('click', () => {});
        
        // Mobile menu
        document.getElementById('mobile-menu-btn')?.addEventListener('click', () => {
            document.getElementById('sidebar').classList.toggle('open');
        });
        
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const page = item.dataset.page;
                this.navigateTo(page);
            });
        });
        
        // Calendar navigation
        document.getElementById('calendar-prev')?.addEventListener('click', () => this.changeMonth(-1));
        document.getElementById('calendar-next')?.addEventListener('click', () => this.changeMonth(1));
        document.getElementById('calendar-today')?.addEventListener('click', () => this.goToToday());
        document.getElementById('calendar-category-filter')?.addEventListener('change', () => this.renderCalendar());
        
        // Task view toggle
        document.getElementById('view-kanban')?.addEventListener('click', () => this.switchTaskView('kanban'));
        document.getElementById('view-list')?.addEventListener('click', () => this.switchTaskView('list'));
        
        // Task filters
        document.getElementById('task-priority-filter')?.addEventListener('change', () => this.loadTasks());
        document.getElementById('task-status-filter')?.addEventListener('change', () => this.loadTasks());
        
        // New buttons
        document.getElementById('new-event-btn')?.addEventListener('click', () => this.openNewEventModal());
        document.getElementById('new-task-btn')?.addEventListener('click', () => this.openNewTaskModal());
        document.getElementById('new-user-btn')?.addEventListener('click', () => this.openNewUserModal());
        
        // Modal close
        document.getElementById('modal-close')?.addEventListener('click', () => this.closeModal());
        document.getElementById('modal-overlay')?.addEventListener('click', (e) => {
            if (e.target === document.getElementById('modal-overlay')) {
                this.closeModal();
            }
        });
    }

    // API Methods
    async api(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (this.token && this.token !== 'test-token') {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const response = await fetch(`${this.apiBase}${endpoint}`, {
            ...options,
            headers,
        });

        if (response.status === 401) {
            throw new Error('Unauthorized');
        }

        // Handle 204 No Content (delete operations)
        if (response.status === 204) {
            return null;
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'An error occurred');
        }

        return data;
    }

    async handleLogin(e) {
        e.preventDefault();
        this.showApp();
    }

    handleLogout() {
        this.showApp();
    }

    async getCurrentUser() {
        // Skip for testing
    }

    // UI Methods
    showLogin() {
        this.showApp();
    }

    showApp() {
        this.updateUserInfo();
        this.checkAdminAccess();
        
        // Set Dashboard as active by default
        const dashboardItem = document.querySelector('.nav-item[data-page="dashboard"]');
        if (dashboardItem) {
            dashboardItem.classList.add('active');
        }
        
        this.navigateTo('dashboard');
    }

    updateUserInfo() {
        if (this.currentUser) {
            document.getElementById('user-name').textContent = this.currentUser.full_name;
            document.getElementById('user-role').textContent = this.currentUser.role.replace('_', ' ');
            document.getElementById('user-initials').textContent = 
                this.currentUser.full_name.split(' ').map(n => n[0]).join('').toUpperCase();
        }
    }

    checkAdminAccess() {
        const adminElements = document.querySelectorAll('.admin-only');
        adminElements.forEach(el => {
            if (this.currentUser?.role !== 'admin') {
                el.classList.add('hidden');
            }
        });
    }

    navigateTo(page) {
        // Remove active class from all menu items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Add active class to selected menu item
        const activeItem = document.querySelector(`.nav-item[data-page="${page}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
        }
        
        // Hide all pages
        document.querySelectorAll('.page-section').forEach(section => {
            section.classList.add('hidden');
        });
        
        // Show selected page
        document.getElementById(`${page}-page`).classList.remove('hidden');
        
        // Update page title in Portuguese
        const titles = {
            'dashboard': 'Painel',
            'calendar': 'Calendário',
            'tasks': 'Tarefas',
            'users': 'Usuários'
        };
        document.getElementById('page-title').textContent = titles[page] || page;
        
        // Close mobile menu
        document.getElementById('sidebar').classList.remove('open');
        
        // Load page data
        this.loadPageData(page);
    }

    async loadPageData(page) {
        switch (page) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'calendar':
                this.renderCalendar();
                this.loadUpcomingEvents();
                break;
            case 'tasks':
                this.loadTasks();
                break;
            case 'users':
                if (this.currentUser?.role === 'admin') {
                    this.loadUsers();
                }
                break;
        }
    }

    updateCurrentDate() {
        const now = new Date();
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        document.getElementById('current-date').textContent = now.toLocaleDateString('pt-BR', options);
    }

    // Dashboard
    async loadDashboard() {
        try {
            const data = await this.api('/dashboard');
            
            // Update metrics
            document.getElementById('metric-active-tasks').textContent = data.metrics.total_active_tasks;
            document.getElementById('metric-completed-week').textContent = data.metrics.tasks_completed_this_week;
            document.getElementById('metric-collections').textContent = data.metrics.upcoming_collections;
            document.getElementById('metric-deliveries').textContent = data.metrics.deliveries_scheduled;
            document.getElementById('metric-overdue').textContent = data.metrics.overdue_tasks;
            document.getElementById('metric-events-today').textContent = data.metrics.events_today;
            
            // Today's tasks
            const tasksList = document.getElementById('dashboard-tasks-list');
            if (data.today_tasks.length > 0) {
                tasksList.innerHTML = data.today_tasks.map(task => this.renderTaskItem(task)).join('');
            } else {
                tasksList.innerHTML = '<div class="text-center text-gray-400 py-4">No tasks for today</div>';
            }
            
            // Upcoming events
            const eventsList = document.getElementById('dashboard-events-list');
            if (data.upcoming_events.length > 0) {
                eventsList.innerHTML = data.upcoming_events.map(event => this.renderEventItem(event)).join('');
            } else {
                eventsList.innerHTML = '<div class="text-center text-gray-400 py-4">No upcoming events</div>';
            }
            
            // Overdue tasks
            const overdueList = document.getElementById('dashboard-overdue-list');
            if (data.overdue_tasks.length > 0) {
                overdueList.innerHTML = data.overdue_tasks.map(task => this.renderTaskItem(task, true)).join('');
            } else {
                overdueList.innerHTML = '<div class="text-center text-gray-400 py-4">No overdue tasks</div>';
            }
        } catch (error) {
            console.error('Error loading dashboard:', error);
        }
    }

    renderTaskItem(task, isOverdue = false) {
        const priorityColors = {
            low: 'bg-blue-500/20 text-blue-400',
            medium: 'bg-amber-500/20 text-amber-400',
            high: 'bg-orange-500/20 text-orange-400',
            critical: 'bg-red-500/20 text-red-400',
        };
        
        const dueDate = task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date';
        const overdueClass = isOverdue ? 'border-l-4 border-l-red-500' : '';
        
        return `
            <div class="flex items-center justify-between p-3 bg-white rounded-lg ${overdueClass}">
                <div class="flex-1">
                    <p class="text-gray-900 font-medium">${task.title}</p>
                    <div class="flex items-center space-x-2 mt-1">
                        <span class="text-xs px-2 py-0.5 rounded ${priorityColors[task.priority]} capitalize">${task.priority}</span>
                        <span class="text-gray-500 text-xs">${dueDate}</span>
                    </div>
                </div>
                ${task.assignee_name ? `<span class="text-gray-400 text-sm">${task.assignee_name}</span>` : ''}
            </div>
        `;
    }

    renderEventItem(event) {
        const categoryColors = {
            collection: 'bg-amber-500/20 text-amber-400',
            production: 'bg-primary-500/20 text-primary-400',
            delivery: 'bg-purple-500/20 text-purple-400',
            training: 'bg-blue-500/20 text-blue-400',
            sales: 'bg-pink-500/20 text-pink-400',
        };
        
        const startDate = new Date(event.start_datetime);
        const endDate = new Date(event.end_datetime);
        const timeStr = `${startDate.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} - ${endDate.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
        
        return `
            <div class="flex items-center justify-between p-3 bg-white rounded-lg">
                <div class="flex-1">
                    <p class="text-gray-900 font-medium">${event.title}</p>
                    <div class="flex items-center space-x-2 mt-1">
                        <span class="text-xs px-2 py-0.5 rounded ${categoryColors[event.category]} capitalize">${event.category}</span>
                        <span class="text-gray-500 text-xs">${timeStr}</span>
                    </div>
                    ${event.location ? `<p class="text-gray-500 text-xs mt-1"><i class="fas fa-map-marker-alt mr-1"></i>${event.location}</p>` : ''}
                </div>
            </div>
        `;
    }

    // Calendar
    changeMonth(delta) {
        this.currentDate.setMonth(this.currentDate.getMonth() + delta);
        this.renderCalendar();
    }

    goToToday() {
        this.currentDate = new Date();
        this.renderCalendar();
    }

    renderCalendar() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'];
        
        document.getElementById('calendar-title').textContent = `${monthNames[month]} ${year}`;
        
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startingDay = firstDay.getDay();
        const totalDays = lastDay.getDate();
        
        const grid = document.getElementById('calendar-grid');
        grid.innerHTML = '';
        
        // Previous month days
        const prevMonthLastDay = new Date(year, month, 0).getDate();
        for (let i = startingDay - 1; i >= 0; i--) {
            const day = prevMonthLastDay - i;
            grid.innerHTML += `
                <div class="min-h-[100px] p-2 border-r border-b border-dark-700 bg-white/50">
                    <span class="text-gray-500 text-sm">${day}</span>
                </div>
            `;
        }
        
        // Current month days
        const today = new Date();
        for (let day = 1; day <= totalDays; day++) {
            const date = new Date(year, month, day);
            const isToday = date.toDateString() === today.toDateString();
            const dateStr = date.toISOString().split('T')[0];
            
            grid.innerHTML += `
                <div class="min-h-[100px] p-2 border-r border-b border-dark-700 ${isToday ? 'bg-primary-900/20' : ''}" data-date="${dateStr}">
                    <span class="${isToday ? 'text-primary-400 font-bold' : 'text-gray-700'} text-sm">${day}</span>
                    <div class="mt-1 space-y-1 calendar-events" data-date="${dateStr}"></div>
                </div>
            `;
        }
        
        // Next month days
        const remainingCells = 42 - (startingDay + totalDays);
        for (let day = 1; day <= remainingCells; day++) {
            grid.innerHTML += `
                <div class="min-h-[100px] p-2 border-r border-b border-dark-700 bg-white/50">
                    <span class="text-gray-500 text-sm">${day}</span>
                </div>
            `;
        }
        
        // Load events for calendar
        this.loadCalendarEvents();
    }

    async loadCalendarEvents() {
        try {
            const category = document.getElementById('calendar-category-filter').value;
            let url = '/events?include_past=false';
            if (category) {
                url += `&category=${category}`;
            }
            
            const events = await this.api(url);
            
            // Group events by date
            const eventsByDate = {};
            events.forEach(event => {
                const dateStr = event.start_datetime.split('T')[0];
                if (!eventsByDate[dateStr]) {
                    eventsByDate[dateStr] = [];
                }
                eventsByDate[dateStr].push(event);
            });
            
            // Render events in calendar
            Object.entries(eventsByDate).forEach(([dateStr, dateEvents]) => {
                const container = document.querySelector(`.calendar-events[data-date="${dateStr}"]`);
                if (container) {
                    const categoryColors = {
                        collection: 'bg-amber-500',
                        production: 'bg-primary-500',
                        delivery: 'bg-purple-500',
                        training: 'bg-blue-500',
                        sales: 'bg-pink-500',
                    };
                    
                    dateEvents.slice(0, 3).forEach(event => {
                        container.innerHTML += `
                            <div class="text-xs px-1.5 py-0.5 rounded ${categoryColors[event.category]} text-gray-900 truncate cursor-pointer" 
                                 title="${event.title}">
                                ${event.title}
                            </div>
                        `;
                    });
                    
                    if (dateEvents.length > 3) {
                        container.innerHTML += `
                            <div class="text-xs text-gray-400 px-1">+${dateEvents.length - 3} more</div>
                        `;
                    }
                }
            });
        } catch (error) {
            console.error('Error loading calendar events:', error);
        }
    }

    async loadUpcomingEvents() {
        try {
            const events = await this.api('/events/upcoming');
            const container = document.getElementById('calendar-events-list');
            
            if (events.length > 0) {
                container.innerHTML = events.map(event => this.renderEventItem(event)).join('');
            } else {
                container.innerHTML = '<div class="text-center text-gray-400 py-8">No upcoming events</div>';
            }
        } catch (error) {
            console.error('Error loading upcoming events:', error);
        }
    }

    // Tasks
    switchTaskView(view) {
        this.currentView = view;
        
        if (view === 'kanban') {
            document.getElementById('kanban-view').classList.remove('hidden');
            document.getElementById('list-view').classList.add('hidden');
            document.getElementById('view-kanban').classList.add('bg-primary-600', 'text-gray-900');
            document.getElementById('view-kanban').classList.remove('bg-gray-800', 'text-gray-700');
            document.getElementById('view-list').classList.remove('bg-primary-600', 'text-gray-900');
            document.getElementById('view-list').classList.add('bg-gray-800', 'text-gray-700');
        } else {
            document.getElementById('kanban-view').classList.add('hidden');
            document.getElementById('list-view').classList.remove('hidden');
            document.getElementById('view-list').classList.add('bg-primary-600', 'text-gray-900');
            document.getElementById('view-list').classList.remove('bg-gray-800', 'text-gray-700');
            document.getElementById('view-kanban').classList.remove('bg-primary-600', 'text-gray-900');
            document.getElementById('view-kanban').classList.add('bg-gray-800', 'text-gray-700');
        }
        
        this.loadTasks();
    }

    async loadTasks() {
        try {
            const priority = document.getElementById('task-priority-filter').value;
            const status = document.getElementById('task-status-filter').value;
            
            let url = '/tasks?include_completed=true';
            if (priority) url += `&priority=${priority}`;
            if (status) url += `&status=${status}`;
            
            const tasks = await this.api(url);
            
            if (this.currentView === 'kanban') {
                this.renderKanban(tasks);
            } else {
                this.renderTaskList(tasks);
            }
        } catch (error) {
            console.error('Error loading tasks:', error);
        }
    }

    renderKanban(tasks) {
        const columns = { pending: [], in_progress: [], completed: [] };

        tasks.forEach(task => {
            if (columns[task.status]) {
                columns[task.status].push(task);
            }
        });

        ['pending', 'in_progress', 'completed'].forEach(status => {
            const container = document.getElementById(`kanban-${status}`);
            const countId = status === 'in_progress' ? 'inprogress-count' : `${status}-count`;
            document.getElementById(countId).textContent = columns[status].length;

            if (columns[status].length > 0) {
                container.innerHTML = columns[status].map(task => this.renderTaskCard(task)).join('');
            } else {
                container.innerHTML = '<div class="text-center text-gray-500 py-8 text-sm">No tasks</div>';
            }
        });
    }

    renderTaskCard(task) {
        const priorityColors = {
            low: 'border-l-blue-500',
            medium: 'border-l-amber-500',
            high: 'border-l-orange-500',
            critical: 'border-l-red-500',
        };

        const dueDate = task.due_date ? new Date(task.due_date).toLocaleDateString() : '';
        const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== 'completed';

        return `
            <div class="task-card bg-white rounded-lg p-4 border-l-4 ${priorityColors[task.priority]} ${isOverdue ? 'ring-1 ring-red-500' : ''} cursor-move"
                 draggable="true"
                 ondragstart="event.dataTransfer.setData('text/plain', ${task.id}); event.target.style.opacity='0.5';"
                 ondragend="event.target.style.opacity='1';">
                <div class="flex items-start justify-between mb-2">
                    <h4 class="font-medium text-gray-900 text-sm">${task.title}</h4>
                    <div class="flex items-center space-x-1">
                        <button onclick="app.openTaskModal(${task.id})" class="text-gray-400 hover:text-gray-900 p-1" title="Edit">
                            <i class="fas fa-edit text-xs"></i>
                        </button>
                        <button onclick="app.deleteTask(${task.id})" class="text-gray-400 hover:text-red-600 p-1" title="Delete">
                            <i class="fas fa-trash text-xs"></i>
                        </button>
                    </div>
                </div>
                ${task.description ? `<p class="text-gray-500 text-xs mb-2 line-clamp-2">${task.description}</p>` : ''}
                <div class="flex items-center justify-between mt-3">
                    <span class="text-xs px-2 py-0.5 rounded bg-gray-200 text-gray-700 capitalize">${task.category}</span>
                    ${dueDate ? `<span class="text-gray-500 text-xs">${dueDate}</span>` : ''}
                </div>
                ${task.assigned_to_id ? `<p class="text-gray-500 text-xs mt-2"><i class="fas fa-user mr-1"></i>User #${task.assigned_to_id}</p>` : ''}
            </div>
        `;
    }

    async deleteTask(taskId) {
        if (!confirm('Are you sure you want to delete this task?')) {
            return;
        }

        try {
            await this.api(`/tasks/${taskId}`, { method: 'DELETE' });
            this.loadTasks();
        } catch (error) {
            alert('Error deleting task: ' + error.message);
        }
    }

    renderTaskList(tasks) {
        const tbody = document.getElementById('tasks-table-body');
        
        if (tasks.length > 0) {
            tbody.innerHTML = tasks.map(task => {
                const priorityColors = {
                    low: 'bg-blue-500/20 text-blue-400',
                    medium: 'bg-amber-500/20 text-amber-400',
                    high: 'bg-orange-500/20 text-orange-400',
                    critical: 'bg-red-500/20 text-red-400',
                };
                
                const statusColors = {
                    pending: 'bg-gray-500/20 text-gray-700',
                    in_progress: 'bg-blue-500/20 text-blue-400',
                    completed: 'bg-primary-500/20 text-primary-400',
                };
                
                const dueDate = task.due_date ? new Date(task.due_date).toLocaleDateString() : '-';
                
                return `
                    <tr class="hover:bg-white/50">
                        <td class="px-6 py-4">
                            <p class="text-gray-900 font-medium">${task.title}</p>
                            ${task.description ? `<p class="text-gray-500 text-sm truncate max-w-xs">${task.description}</p>` : ''}
                        </td>
                        <td class="px-6 py-4">
                            <span class="text-xs px-2 py-1 rounded ${priorityColors[task.priority]} capitalize">${task.priority}</span>
                        </td>
                        <td class="px-6 py-4">
                            <span class="text-xs px-2 py-1 rounded ${statusColors[task.status]} capitalize">${task.status.replace('_', ' ')}</span>
                        </td>
                        <td class="px-6 py-4">
                            <span class="text-gray-700 text-sm capitalize">${task.category}</span>
                        </td>
                        <td class="px-6 py-4">
                            <span class="text-gray-700 text-sm">${dueDate}</span>
                        </td>
                        <td class="px-6 py-4">
                            ${task.assignee ? `<span class="text-gray-700 text-sm">${task.assignee.full_name}</span>` : '<span class="text-gray-500 text-sm">-</span>'}
                        </td>
                        <td class="px-6 py-4 text-right">
                            <button onclick="app.openTaskModal(${task.id})" class="text-primary-500 hover:text-primary-400 text-sm">Edit</button>
                        </td>
                    </tr>
                `;
            }).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-gray-400 py-8">No tasks found</td></tr>';
        }
    }

    // Users
    async loadUsers() {
        try {
            this.users = await this.api('/auth/users');
            const tbody = document.getElementById('users-table-body');
            
            if (this.users.length > 0) {
                tbody.innerHTML = this.users.map(user => {
                    const roleColors = {
                        admin: 'bg-red-500/20 text-red-400',
                        operations_manager: 'bg-purple-500/20 text-purple-400',
                        field_staff: 'bg-blue-500/20 text-blue-400',
                        sales: 'bg-pink-500/20 text-pink-400',
                    };
                    
                    const createdDate = new Date(user.created_at).toLocaleDateString();
                    
                    return `
                        <tr class="hover:bg-white/50">
                            <td class="px-6 py-4">
                                <div class="flex items-center">
                                    <div class="w-8 h-8 rounded-full bg-primary-600/20 flex items-center justify-center mr-3">
                                        <span class="text-primary-500 text-sm font-medium">${user.full_name.split(' ').map(n => n[0]).join('').toUpperCase()}</span>
                                    </div>
                                    <span class="text-gray-900 font-medium">${user.full_name}</span>
                                </div>
                            </td>
                            <td class="px-6 py-4">
                                <span class="text-gray-700 text-sm">${user.email}</span>
                            </td>
                            <td class="px-6 py-4">
                                <span class="text-xs px-2 py-1 rounded ${roleColors[user.role]} capitalize">${user.role.replace('_', ' ')}</span>
                            </td>
                            <td class="px-6 py-4">
                                <span class="text-xs px-2 py-1 rounded ${user.is_active ? 'bg-primary-500/20 text-primary-400' : 'bg-red-500/20 text-red-400'}">
                                    ${user.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </td>
                            <td class="px-6 py-4">
                                <span class="text-gray-700 text-sm">${createdDate}</span>
                            </td>
                            <td class="px-6 py-4 text-right">
                                <button onclick="app.editUser(${user.id})" class="text-primary-500 hover:text-primary-400 text-sm mr-3">Edit</button>
                                ${user.id !== this.currentUser.id ? `<button onclick="app.deleteUser(${user.id})" class="text-red-500 hover:text-red-400 text-sm">Delete</button>` : ''}
                            </td>
                        </tr>
                    `;
                }).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center text-gray-400 py-8">No users found</td></tr>';
            }
        } catch (error) {
            console.error('Error loading users:', error);
        }
    }

    // Modals
    openModal(title, content) {
        document.getElementById('modal-title').textContent = title;
        document.getElementById('modal-content').innerHTML = content;
        document.getElementById('modal-overlay').classList.remove('hidden');
    }

    closeModal() {
        document.getElementById('modal-overlay').classList.add('hidden');
    }

    openNewEventModal() {
        const content = `
            <form id="event-form" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Title *</label>
                    <input type="text" name="title" required class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
                    <textarea name="description" rows="3" class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900"></textarea>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Location</label>
                    <input type="text" name="location" class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Start Date & Time *</label>
                        <input type="datetime-local" name="start_datetime" required class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">End Date & Time *</label>
                        <input type="datetime-local" name="end_datetime" required class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                    </div>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Category *</label>
                    <select name="category" required class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                        <option value="collection">Collection</option>
                        <option value="production">Production</option>
                        <option value="delivery">Delivery</option>
                        <option value="training">Training</option>
                        <option value="sales">Sales</option>
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Assign Staff</label>
                    <select name="assigned_staff_ids" multiple class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900 h-32">
                        ${this.users.map(u => `<option value="${u.id}">${u.full_name}</option>`).join('')}
                    </select>
                    <p class="text-gray-500 text-xs mt-1">Hold Ctrl/Cmd to select multiple</p>
                </div>
                <div class="flex justify-end space-x-3 pt-4">
                    <button type="button" onclick="app.closeModal()" class="px-4 py-2 bg-gray-200 hover:bg-gray-600 text-gray-900 rounded-lg transition-colors">Cancel</button>
                    <button type="submit" class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-gray-900 rounded-lg transition-colors">Create Event</button>
                </div>
            </form>
        `;
        
        this.openModal('Create New Event', content);
        
        document.getElementById('event-form')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = {
                title: formData.get('title'),
                description: formData.get('description'),
                location: formData.get('location'),
                start_datetime: formData.get('start_datetime'),
                end_datetime: formData.get('end_datetime'),
                category: formData.get('category'),
                assigned_staff_ids: formData.getAll('assigned_staff_ids').map(Number),
            };
            
            try {
                await this.api('/events', { method: 'POST', body: JSON.stringify(data) });
                this.closeModal();
                this.renderCalendar();
                this.loadUpcomingEvents();
            } catch (error) {
                alert(error.message);
            }
        });
    }

    openNewTaskModal() {
        const content = `
            <form id="task-form" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Title *</label>
                    <input type="text" name="title" required class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
                    <textarea name="description" rows="3" class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900"></textarea>
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Priority *</label>
                        <select name="priority" required class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                            <option value="low">Low</option>
                            <option value="medium" selected>Medium</option>
                            <option value="high">High</option>
                            <option value="critical">Critical</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Category *</label>
                        <select name="category" required class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                            <option value="collection">Collection</option>
                            <option value="production">Production</option>
                            <option value="delivery">Delivery</option>
                            <option value="training">Training</option>
                            <option value="sales">Sales</option>
                            <option value="admin">Admin</option>
                        </select>
                    </div>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Due Date</label>
                    <input type="datetime-local" name="due_date" class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Assign To</label>
                    <select name="assigned_to_id" class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                        <option value="">Unassigned</option>
                        ${this.users.map(u => `<option value="${u.id}">${u.full_name}</option>`).join('')}
                    </select>
                </div>
                <div class="flex justify-end space-x-3 pt-4">
                    <button type="button" onclick="app.closeModal()" class="px-4 py-2 bg-gray-200 hover:bg-gray-600 text-gray-900 rounded-lg transition-colors">Cancel</button>
                    <button type="submit" class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-gray-900 rounded-lg transition-colors">Create Task</button>
                </div>
            </form>
        `;
        
        this.openModal('Create New Task', content);
        
        document.getElementById('task-form')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const dueDateValue = formData.get('due_date');
            const data = {
                title: formData.get('title'),
                description: formData.get('description'),
                priority: formData.get('priority'),
                category: formData.get('category'),
                assigned_to_id: formData.get('assigned_to_id') ? parseInt(formData.get('assigned_to_id')) : null,
            };
            
            // Only add due_date if it has a value
            if (dueDateValue) {
                data.due_date = dueDateValue;
            }

            try {
                await this.api('/tasks', { method: 'POST', body: JSON.stringify(data) });
                this.closeModal();
                this.loadTasks();
            } catch (error) {
                alert(error.message);
            }
        });
    }

    async openTaskModal(taskId) {
        try {
            const task = await this.api(`/tasks/${taskId}`);
            
            const content = `
                <form id="edit-task-form" class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Title *</label>
                        <input type="text" name="title" value="${task.title}" required class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
                        <textarea name="description" rows="3" class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">${task.description || ''}</textarea>
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Priority *</label>
                            <select name="priority" required class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                                <option value="low" ${task.priority === 'low' ? 'selected' : ''}>Low</option>
                                <option value="medium" ${task.priority === 'medium' ? 'selected' : ''}>Medium</option>
                                <option value="high" ${task.priority === 'high' ? 'selected' : ''}>High</option>
                                <option value="critical" ${task.priority === 'critical' ? 'selected' : ''}>Critical</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Status *</label>
                            <select name="status" required class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                                <option value="pending" ${task.status === 'pending' ? 'selected' : ''}>Pending</option>
                                <option value="in_progress" ${task.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                                <option value="completed" ${task.status === 'completed' ? 'selected' : ''}>Completed</option>
                            </select>
                        </div>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Category *</label>
                        <select name="category" required class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                            <option value="collection" ${task.category === 'collection' ? 'selected' : ''}>Collection</option>
                            <option value="production" ${task.category === 'production' ? 'selected' : ''}>Production</option>
                            <option value="delivery" ${task.category === 'delivery' ? 'selected' : ''}>Delivery</option>
                            <option value="training" ${task.category === 'training' ? 'selected' : ''}>Training</option>
                            <option value="sales" ${task.category === 'sales' ? 'selected' : ''}>Sales</option>
                            <option value="admin" ${task.category === 'admin' ? 'selected' : ''}>Admin</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Due Date</label>
                        <input type="datetime-local" name="due_date" value="${task.due_date ? new Date(task.due_date).toISOString().slice(0, 16) : ''}" class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Assign To</label>
                        <select name="assigned_to_id" class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                            <option value="">Unassigned</option>
                            ${this.users.map(u => `<option value="${u.id}" ${task.assigned_to_id === u.id ? 'selected' : ''}>${u.full_name}</option>`).join('')}
                        </select>
                    </div>
                    <div class="flex justify-end space-x-3 pt-4">
                        <button type="button" onclick="app.closeModal()" class="px-4 py-2 bg-gray-200 hover:bg-gray-600 text-gray-900 rounded-lg transition-colors">Cancel</button>
                        <button type="submit" class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-gray-900 rounded-lg transition-colors">Save Changes</button>
                    </div>
                </form>
            `;
            
            this.openModal(`Edit Task: ${task.title}`, content);
            
            document.getElementById('edit-task-form')?.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const dueDateValue = formData.get('due_date');
                const data = {
                    title: formData.get('title'),
                    description: formData.get('description'),
                    priority: formData.get('priority'),
                    status: formData.get('status'),
                    category: formData.get('category'),
                    assigned_to_id: formData.get('assigned_to_id') ? parseInt(formData.get('assigned_to_id')) : null,
                };
                
                // Only add due_date if it has a value
                if (dueDateValue) {
                    data.due_date = dueDateValue;
                }

                try {
                    await this.api(`/tasks/${taskId}`, { method: 'PUT', body: JSON.stringify(data) });
                    this.closeModal();
                    this.loadTasks();
                } catch (error) {
                    alert(error.message);
                }
            });
        } catch (error) {
            alert(error.message);
        }
    }

    openNewUserModal() {
        const content = `
            <form id="user-form" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Full Name *</label>
                    <input type="text" name="full_name" required class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Email *</label>
                    <input type="email" name="email" required class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Password *</label>
                    <input type="password" name="password" required minlength="8" class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Role *</label>
                    <select name="role" required class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                        <option value="field_staff">Field Staff</option>
                        <option value="sales">Sales</option>
                        <option value="operations_manager">Operations Manager</option>
                        <option value="admin">Admin</option>
                    </select>
                </div>
                <div class="flex justify-end space-x-3 pt-4">
                    <button type="button" onclick="app.closeModal()" class="px-4 py-2 bg-gray-200 hover:bg-gray-600 text-gray-900 rounded-lg transition-colors">Cancel</button>
                    <button type="submit" class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-gray-900 rounded-lg transition-colors">Create User</button>
                </div>
            </form>
        `;
        
        this.openModal('Create New User', content);
        
        document.getElementById('user-form')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = {
                full_name: formData.get('full_name'),
                email: formData.get('email'),
                password: formData.get('password'),
                role: formData.get('role'),
            };
            
            try {
                await this.api('/auth/users', { method: 'POST', body: JSON.stringify(data) });
                this.closeModal();
                this.loadUsers();
            } catch (error) {
                alert(error.message);
            }
        });
    }

    async editUser(userId) {
        const user = this.users.find(u => u.id === userId);
        if (!user) return;
        
        const content = `
            <form id="edit-user-form" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Full Name *</label>
                    <input type="text" name="full_name" value="${user.full_name}" required class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Email *</label>
                    <input type="email" name="email" value="${user.email}" required class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Role *</label>
                    <select name="role" required class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                        <option value="field_staff" ${user.role === 'field_staff' ? 'selected' : ''}>Field Staff</option>
                        <option value="sales" ${user.role === 'sales' ? 'selected' : ''}>Sales</option>
                        <option value="operations_manager" ${user.role === 'operations_manager' ? 'selected' : ''}>Operations Manager</option>
                        <option value="admin" ${user.role === 'admin' ? 'selected' : ''}>Admin</option>
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
                    <select name="is_active" class="w-full px-4 py-2 bg-white border border-gray-300 rounded-lg focus:outline-none focus:border-primary-500 text-gray-900">
                        <option value="true" ${user.is_active ? 'selected' : ''}>Active</option>
                        <option value="false" ${!user.is_active ? 'selected' : ''}>Inactive</option>
                    </select>
                </div>
                <div class="flex justify-end space-x-3 pt-4">
                    <button type="button" onclick="app.closeModal()" class="px-4 py-2 bg-gray-200 hover:bg-gray-600 text-gray-900 rounded-lg transition-colors">Cancel</button>
                    <button type="submit" class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-gray-900 rounded-lg transition-colors">Save Changes</button>
                </div>
            </form>
        `;
        
        this.openModal(`Edit User: ${user.full_name}`, content);
        
        document.getElementById('edit-user-form')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = {
                full_name: formData.get('full_name'),
                email: formData.get('email'),
                role: formData.get('role'),
                is_active: formData.get('is_active') === 'true',
            };
            
            try {
                await this.api(`/auth/users/${userId}`, { method: 'PUT', body: JSON.stringify(data) });
                this.closeModal();
                this.loadUsers();
            } catch (error) {
                alert(error.message);
            }
        });
    }

    async deleteUser(userId) {
        if (!confirm('Are you sure you want to delete this user?')) return;
        
        try {
            await this.api(`/auth/users/${userId}`, { method: 'DELETE' });
            this.loadUsers();
        } catch (error) {
            alert(error.message);
        }
    }
}

// Initialize app
const app = new XaneneOps();
