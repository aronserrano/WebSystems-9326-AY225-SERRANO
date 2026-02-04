// ==========================================
// NAVIGATION FUNCTIONALITY
// ==========================================

// Mobile navigation toggle
document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('active');
            }
        });
    }

    // Initialize page-specific functionality
    initializeProgramsPage();
    initializeFacultyPage();
    initializeAnnouncementsPage();
    initializeContactForm();
});

// ==========================================
// PROGRAMS PAGE - TABS AND ACCORDION
// ==========================================

function initializeProgramsPage() {
    // Check if we're on the programs page
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    if (tabButtons.length === 0) return;

    // Tab switching functionality
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');

            // Remove active class from all buttons and panels
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanels.forEach(panel => panel.classList.remove('active'));

            // Add active class to clicked button and corresponding panel
            this.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });

    // Accordion functionality
    const accordionHeaders = document.querySelectorAll('.accordion-header');

    accordionHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const accordionItem = this.parentElement;
            const isActive = accordionItem.classList.contains('active');

            // Close all accordion items in the same accordion
            const accordion = accordionItem.closest('.accordion');
            accordion.querySelectorAll('.accordion-item').forEach(item => {
                item.classList.remove('active');
            });

            // Toggle current item
            if (!isActive) {
                accordionItem.classList.add('active');
            }
        });
    });
}

// ==========================================
// FACULTY PAGE - FILTERING AND SEARCH
// ==========================================

// Faculty data
const facultyData = [
    {
        name: "Dr. Maria Santos",
        department: "cs",
        departmentName: "Computer Science",
        specialization: "Artificial Intelligence, Machine Learning",
        email: "maria.santos@ccs.edu",
        phone: "(123) 456-7801",
        initial: "MS"
    },
    {
        name: "Prof. John Reyes",
        department: "cs",
        departmentName: "Computer Science",
        specialization: "Software Engineering, Algorithms",
        email: "john.reyes@ccs.edu",
        phone: "(123) 456-7802",
        initial: "JR"
    },
    {
        name: "Dr. Angela Cruz",
        department: "cs",
        departmentName: "Computer Science",
        specialization: "Database Systems, Data Mining",
        email: "angela.cruz@ccs.edu",
        phone: "(123) 456-7803",
        initial: "AC"
    },
    {
        name: "Prof. Robert Tan",
        department: "it",
        departmentName: "Information Technology",
        specialization: "Network Security, Cloud Computing",
        email: "robert.tan@ccs.edu",
        phone: "(123) 456-7804",
        initial: "RT"
    },
    {
        name: "Dr. Lisa Garcia",
        department: "it",
        departmentName: "Information Technology",
        specialization: "Web Development, Mobile Applications",
        email: "lisa.garcia@ccs.edu",
        phone: "(123) 456-7805",
        initial: "LG"
    },
    {
        name: "Prof. Michael Lopez",
        department: "it",
        departmentName: "Information Technology",
        specialization: "Systems Administration, DevOps",
        email: "michael.lopez@ccs.edu",
        phone: "(123) 456-7806",
        initial: "ML"
    },
    {
        name: "Dr. Patricia Ramos",
        department: "is",
        departmentName: "Information Systems",
        specialization: "Business Analytics, ERP Systems",
        email: "patricia.ramos@ccs.edu",
        phone: "(123) 456-7807",
        initial: "PR"
    },
    {
        name: "Prof. David Mendoza",
        department: "is",
        departmentName: "Information Systems",
        specialization: "Systems Analysis, Project Management",
        email: "david.mendoza@ccs.edu",
        phone: "(123) 456-7808",
        initial: "DM"
    },
    {
        name: "Dr. Sarah Villanueva",
        department: "is",
        departmentName: "Information Systems",
        specialization: "Business Intelligence, Data Visualization",
        email: "sarah.villanueva@ccs.edu",
        phone: "(123) 456-7809",
        initial: "SV"
    },
    {
        name: "Prof. James Bautista",
        department: "cs",
        departmentName: "Computer Science",
        specialization: "Computer Graphics, Game Development",
        email: "james.bautista@ccs.edu",
        phone: "(123) 456-7810",
        initial: "JB"
    },
    {
        name: "Dr. Catherine Morales",
        department: "it",
        departmentName: "Information Technology",
        specialization: "Cybersecurity, Ethical Hacking",
        email: "catherine.morales@ccs.edu",
        phone: "(123) 456-7811",
        initial: "CM"
    },
    {
        name: "Prof. Anthony Flores",
        department: "is",
        departmentName: "Information Systems",
        specialization: "Digital Transformation, IT Strategy",
        email: "anthony.flores@ccs.edu",
        phone: "(123) 456-7812",
        initial: "AF"
    }
];

function initializeFacultyPage() {
    const facultyGrid = document.getElementById('facultyGrid');
    if (!facultyGrid) return;

    const searchInput = document.getElementById('facultySearch');
    const filterButtons = document.querySelectorAll('.filter-btn');
    const noResults = document.getElementById('noResults');

    let currentFilter = 'all';
    let currentSearch = '';

    // Display all faculty initially
    displayFaculty(facultyData);

    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            currentSearch = e.target.value.toLowerCase();
            filterAndDisplayFaculty();
        });
    }

    // Filter functionality
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            currentFilter = this.getAttribute('data-department');
            filterAndDisplayFaculty();
        });
    });

    function filterAndDisplayFaculty() {
        let filteredData = facultyData;

        // Apply department filter
        if (currentFilter !== 'all') {
            filteredData = filteredData.filter(faculty => faculty.department === currentFilter);
        }

        // Apply search filter
        if (currentSearch) {
            filteredData = filteredData.filter(faculty => 
                faculty.name.toLowerCase().includes(currentSearch) ||
                faculty.specialization.toLowerCase().includes(currentSearch) ||
                faculty.departmentName.toLowerCase().includes(currentSearch)
            );
        }

        displayFaculty(filteredData);

        // Show/hide no results message
        if (filteredData.length === 0) {
            noResults.style.display = 'block';
        } else {
            noResults.style.display = 'none';
        }
    }

    function displayFaculty(data) {
        facultyGrid.innerHTML = '';

        data.forEach(faculty => {
            const card = document.createElement('div');
            card.className = 'faculty-card';
            card.innerHTML = `
                <div class="faculty-image">
                    ${faculty.initial}
                </div>
                <div class="faculty-info">
                    <h3>${faculty.name}</h3>
                    <div class="faculty-department">${faculty.departmentName}</div>
                    <div class="faculty-specialization">${faculty.specialization}</div>
                    <div class="faculty-contact">
                        📧 ${faculty.email}<br>
                        📞 ${faculty.phone}
                    </div>
                </div>
            `;
            facultyGrid.appendChild(card);
        });
    }
}

// ==========================================
// ANNOUNCEMENTS PAGE - DYNAMIC BOARD
// ==========================================

// Announcements data
const announcementsData = [
    {
        id: 1,
        title: "Enrollment for Second Semester 2024-2025",
        category: "academic",
        date: "2024-11-15",
        content: "Enrollment for the second semester will begin on December 1, 2024. All students are advised to prepare their requirements and consult with their advisers. Online enrollment will be available through the student portal. Early enrollment is encouraged to secure your class schedule."
    },
    {
        id: 2,
        title: "Tech Innovation Summit 2024",
        category: "events",
        date: "2024-11-20",
        content: "Join us for the annual Tech Innovation Summit on December 15, 2024, at the University Auditorium. This year's theme is 'AI and the Future of Computing.' Industry leaders and innovators will share insights on emerging technologies. Registration is free for all CCS students."
    },
    {
        id: 3,
        title: "Cybersecurity Workshop Series",
        category: "seminars",
        date: "2024-11-10",
        content: "The College of Computer Studies is hosting a three-part workshop series on Cybersecurity Fundamentals. Sessions will be held every Friday starting November 22. Topics include network security, ethical hacking, and data protection. Limited slots available. Register at the CCS office."
    },
    {
        id: 4,
        title: "Midterm Examination Schedule",
        category: "academic",
        date: "2024-11-01",
        content: "Midterm examinations for all programs will be held from November 25-29, 2024. Students are reminded to check the examination schedule posted on the bulletin board and online portal. Make sure to bring valid ID and other required materials during exams."
    },
    {
        id: 5,
        title: "Hackathon 2024: Code for Change",
        category: "events",
        date: "2024-11-18",
        content: "CCS is organizing a 48-hour hackathon on December 8-10, 2024. Form teams of 3-5 members and develop innovative solutions for social good. Exciting prizes await the winners! Registration deadline is November 30. Visit our website for more details and registration."
    },
    {
        id: 6,
        title: "Guest Lecture: Machine Learning in Practice",
        category: "seminars",
        date: "2024-11-12",
        content: "Dr. Emmanuel Rodriguez from Tech Corp will deliver a guest lecture on 'Practical Applications of Machine Learning' on November 28, 2024, at 2:00 PM in Room 301. This is an excellent opportunity to learn from industry experts. All students are welcome to attend."
    },
    {
        id: 7,
        title: "Library Hours Extension During Finals Week",
        category: "general",
        date: "2024-11-08",
        content: "The CCS Computer Laboratory will extend operating hours during finals week (December 9-13). The lab will be open from 7:00 AM to 10:00 PM to accommodate students who need to work on their projects and review for examinations."
    },
    {
        id: 8,
        title: "Internship Opportunities for 3rd Year Students",
        category: "general",
        date: "2024-11-05",
        content: "Several partner companies are offering internship opportunities for third-year students. Positions available in software development, IT support, and business analysis. Interested students should submit their resume and transcript of records to the CCS Career Services Office by November 30."
    }
];

function initializeAnnouncementsPage() {
    const container = document.getElementById('announcementsContainer');
    if (!container) return;

    const filterButtons = document.querySelectorAll('.announcement-filter-btn');
    let currentCategory = 'all';

    // Display all announcements initially
    displayAnnouncements(announcementsData);

    // Filter functionality
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            currentCategory = this.getAttribute('data-category');
            
            if (currentCategory === 'all') {
                displayAnnouncements(announcementsData);
            } else {
                const filtered = announcementsData.filter(
                    announcement => announcement.category === currentCategory
                );
                displayAnnouncements(filtered);
            }
        });
    });

    function displayAnnouncements(data) {
        container.innerHTML = '';

        data.forEach(announcement => {
            const card = document.createElement('div');
            card.className = 'announcement-card';
            card.innerHTML = `
                <div class="announcement-header">
                    <div>
                        <h3 class="announcement-title">${announcement.title}</h3>
                        <span class="announcement-category">${formatCategory(announcement.category)}</span>
                    </div>
                    <div class="announcement-date">${formatDate(announcement.date)}</div>
                </div>
                <div class="announcement-content">
                    ${announcement.content}
                </div>
            `;
            container.appendChild(card);
        });
    }

    function formatCategory(category) {
        return category.charAt(0).toUpperCase() + category.slice(1);
    }

    function formatDate(dateString) {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return new Date(dateString).toLocaleDateString('en-US', options);
    }
}

// ==========================================
// CONTACT FORM - VALIDATION
// ==========================================

function initializeContactForm() {
    const form = document.getElementById('contactForm');
    if (!form) return;

    const nameInput = document.getElementById('name');
    const emailInput = document.getElementById('email');
    const subjectInput = document.getElementById('subject');
    const inquiryTypeInput = document.getElementById('inquiryType');
    const messageInput = document.getElementById('message');
    const formMsg = document.getElementById('formMsg');

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Reset previous error messages
        clearErrors();

        // Validate form
        let isValid = true;

        // Name validation
        if (!nameInput.value.trim()) {
            showError('nameError', 'Name is required');
            isValid = false;
        } else if (nameInput.value.trim().length < 2) {
            showError('nameError', 'Name must be at least 2 characters');
            isValid = false;
        }

        // Email validation
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailInput.value.trim()) {
            showError('emailError', 'Email is required');
            isValid = false;
        } else if (!emailPattern.test(emailInput.value)) {
            showError('emailError', 'Please enter a valid email address');
            isValid = false;
        }

        // Subject validation
        if (!subjectInput.value.trim()) {
            showError('subjectError', 'Subject is required');
            isValid = false;
        } else if (subjectInput.value.trim().length < 5) {
            showError('subjectError', 'Subject must be at least 5 characters');
            isValid = false;
        }

        // Inquiry type validation
        if (!inquiryTypeInput.value) {
            showError('inquiryTypeError', 'Please select an inquiry type');
            isValid = false;
        }

        // Message validation
        if (!messageInput.value.trim()) {
            showError('messageError', 'Message is required');
            isValid = false;
        } else if (messageInput.value.trim().length < 10) {
            showError('messageError', 'Message must be at least 10 characters');
            isValid = false;
        }

        // If form is valid, show success message
        if (isValid) {
            formMsg.textContent = 'Message sent successfully! We will get back to you soon.';
            formMsg.className = 'form-message success';
            form.reset();

            // Hide success message after 5 seconds
            setTimeout(() => {
                formMsg.style.display = 'none';
            }, 5000);
        } else {
            formMsg.textContent = 'Please correct the errors above and try again.';
            formMsg.className = 'form-message error';
        }
    });

    // Real-time validation on input
    nameInput.addEventListener('blur', function() {
        if (!this.value.trim()) {
            showError('nameError', 'Name is required');
        } else if (this.value.trim().length < 2) {
            showError('nameError', 'Name must be at least 2 characters');
        } else {
            clearError('nameError');
        }
    });

    emailInput.addEventListener('blur', function() {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!this.value.trim()) {
            showError('emailError', 'Email is required');
        } else if (!emailPattern.test(this.value)) {
            showError('emailError', 'Please enter a valid email address');
        } else {
            clearError('emailError');
        }
    });

    subjectInput.addEventListener('blur', function() {
        if (!this.value.trim()) {
            showError('subjectError', 'Subject is required');
        } else if (this.value.trim().length < 5) {
            showError('subjectError', 'Subject must be at least 5 characters');
        } else {
            clearError('subjectError');
        }
    });

    inquiryTypeInput.addEventListener('change', function() {
        if (!this.value) {
            showError('inquiryTypeError', 'Please select an inquiry type');
        } else {
            clearError('inquiryTypeError');
        }
    });

    messageInput.addEventListener('blur', function() {
        if (!this.value.trim()) {
            showError('messageError', 'Message is required');
        } else if (this.value.trim().length < 10) {
            showError('messageError', 'Message must be at least 10 characters');
        } else {
            clearError('messageError');
        }
    });

    function showError(elementId, message) {
        const errorElement = document.getElementById(elementId);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
    }

    function clearError(elementId) {
        const errorElement = document.getElementById(elementId);
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.style.display = 'none';
        }
    }

    function clearErrors() {
        const errorElements = document.querySelectorAll('.error-message');
        errorElements.forEach(element => {
            element.textContent = '';
            element.style.display = 'none';
        });
        formMsg.style.display = 'none';
    }
}